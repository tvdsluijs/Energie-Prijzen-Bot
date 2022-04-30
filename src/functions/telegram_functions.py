from ast import Constant
import code
import os
import telegram
from time import time
from telegram.ext import Updater, CommandHandler
from functions.energieprijzen import EnergiePrijzen
from functions.energieprijzen_sql import EnergiePrijzen_SQL
from datetime import datetime

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Telegram_Functions(object):
    ENERGIE = Constant(1)
    GAS = Constant(2)

    def __init__(self, *args, **kwargs) -> None:
        try:
            self.dbname = kwargs['dbname']
            self.telegram_key = kwargs['telegram_key']
            self.admin_ids = kwargs['admin_ids']
            self.path = kwargs['path']
            self.startTime = kwargs['startTime']

            self.date_hours = []
            self.dontunderstand_text = "Sorry, ik heb je niet begrepen, zocht je naar /hulp ?"

            self.commando_hulp = """

Je hebt de volgende commando's tot je beschikking:

/voegmetoe → Je chat-id toevoegen
/verwijderme → Je chat-id verwijderen
/mijnid → Je chat-id tonen
/nu → huidige prijzen dit uur
/vandaag → prijzen van vandaag
/morgen → prijzen van morgen (na 15.00)
/laag → Laagste prijzen van vandaag
/hoog → Hoogste prijzen van vandaag
/system → Wat systeem gegevens"""

            self.help_tekst = """
Let op: alle bedragen zijn kale inkoopprijzen, dus zonder opslag, BTW en belastingen.

Voor overzicht van alle /commandos.

/voegmetoe voor automatische berichten:
- de laagste prijzen van morgen;
- bericht voordat laagste prijs begint;
- informatie over prijzen onder 0.

Vergeet niet te doneren
/doneer

Vragen?
Mail naar info@itheo.tech
"""

            self.admin_help = """

Dit is de Admin help
/fill → vul de database met historische data
/listids → lijst met aangemelde personen
/onderhoud aan → stuur iedereen een onderhoud bericht
/onderhoud uit → stuur iedereen een onderhoud bericht
/system → wat systeem informatie
/nexthourminus → is there a minus price next hour
/tomorrowminus → tomorrows 0 and below prices
            """
            super().__init__()
        except KeyError as e:
            log.error(e)
        except Exception as e:
            log.critical(e)

    def start_me_up(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            first_name = update.message.chat.first_name
            username = update.message.chat.username

            if first_name is None or first_name == "":
                name = username
            else:
                name = username

            msg = f"""Beste {name},
welkom bij de Energie prijzen bot
{self.help_tekst}
"""

            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='Markdown')
        except Exception as e:
            log.error(e)

    def commandos(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            context.bot.send_message(chat_id=update.message.chat_id, text=self.commando_hulp, parse_mode='Markdown')
        except Exception as e:
            log.error(e)
    def help_me(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            first_name = update.message.chat.first_name
            username = update.message.chat.username

            if first_name is None or first_name == "":
                name = username
            else:
                name = username

            msg = f"""Hoi {name},
ik ben hier om je te helpen
{self.help_tekst}
"""
            # msg = telegram.utils.helpers.escape_markdown(msg, 2)
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='Markdown')
        except Exception as e:
            log.error(e)


    def donate(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = "https://donorbox.org/tvdsluijs-github"
            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def call_energiebot(self, context: telegram.ext.CallbackContext):
        try:
            #update prices
            #at 16hour do a send lowest prices overview
            #every hour send a at next hour you will have the lowest prices
            now = datetime.now()
            date_hour = now.strftime("%Y-%m-%d %H:00")

            # Check if current hour in list
            if date_hour in self.date_hours:
                return

            # hour not in list so do somehtings
            self.date_hours.append(date_hour) # add hour to list
            self.date_hours = self.date_hours[-5:] # remove last hour

            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()

            #stroom = 1, gas 2 2
            for sg in [1,2]:
                data = EP.get_energyzero_data(kind=sg)
                EP.save_data(data=data, kind=sg)

            cur_hour = int(now.strftime("%H"))
            if cur_hour not in [23,0,1,2,3,4,5,6]:
                ids = self.get_users()
                # if (msg := EP.get_next_hour_lowest_price()):
                #     for id in ids:
                #         if id == 0:
                #             continue
                #         context.bot.send_message(chat_id=id, text=msg)

                if (msg := EP.get_next_hour_minus_price()):
                    for id in ids:
                        if id == 0:
                            continue
                        context.bot.send_message(chat_id=id, text=msg)

                if int(EP.current_hour_short) == 16:
                    if (msg := EP.get_tomorrows_minus_price()):
                        for id in ids:
                            if id == 0:
                                continue
                            context.bot.send_message(chat_id=id, text=msg, parse_mode='MarkdownV2')
            EP = None
        except Exception as e:
            log.error(e)

    def get_users(self) -> list:
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            ids = []
            ids = esql.get_users()
            ids.append(0)
            esql = None
            return ids
        except Exception as e:
            log.error(e)

    def blahblah(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = "Sorry, ik werk alleen met commando's, zoek je /hulp ?"
            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def dontunderstand(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        # https://blog.finxter.com/python-telegram-bot/
        try:
            msg = self.dontunderstand_text
            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def add_me(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            mss_id = esql.add_user(user_id=update.message.chat_id)
            esql = None
            match mss_id:
                case 0:
                    msg = f"Jouw user chat id ({update.message.chat_id}) staat al in het systeem"
                case 1:
                    msg = f"Ik heb je toegevoegd met user chat id: {update.message.chat_id}! Vanaf nu ontvang je de energie prijzen"
                case -1:
                    msg = f"Ai... we hebben een probleem om je toe te voegen met user chat id ({update.message.chat_id}), probeer het nog een keer of stuur een mail naar info@itheo.tech als dit probleem blijft"

            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def remove_me(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            mss_id = esql.remove_user(user_id=update.message.chat_id)
            esql = None
            msg = "Oeps... er ging iets fout"

            match mss_id:
                case 0:
                    msg = f"Jouw user chat id ({update.message.chat_id}) is niet gevonden, dus verwijderen kan niet"
                case 1:
                    msg = f"Jouw user chat id ({update.message.chat_id}) is verwijdert! Je ontvangt nu geen automatische energie updates"
                case -1:
                    msg = f"Ai... we hebben een probleem om jouw user chat id ({update.message.chat_id}) te verwijderen, probeer het nog een keer of stuur een mail naar info@itheo.tech als dit probleem blijft"

            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def get_id(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = f"Jouw user chat id is {update.message.chat_id}!"
            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def get_today(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_todays_prices(date=EP.today)
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)

    def get_tomorrow(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            if int(EP.current_hour_short) < 15:
                msg = """Prijzen van morgen zijn pas na 15u beschikbaar"""
            else:
                msg = EP.get_todays_prices(date=EP.enddate)
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)

    def get_current(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_cur_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)

    def get_highprices(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_todays_highest_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)

    def get_lowprices(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_todays_lowest_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)

    # some admin functions

    def tomorrowminus(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_tomorrows_minus_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)

    def nexthourminus(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_next_hour_lowest_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')
        except Exception as e:
            log.error(e)


    def systeminfo(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = self.dontunderstand_text
            # if int(update.message.chat_id) in self.admin_ids:
            versie_path = os.path.join(self.path, "VERSION.TXT")
            version = open(versie_path, "r").read().replace('\n','')
            dbsize = self.fileSize(self.dbname)
            seconds = int(time() - self.startTime)
            uptime = self.secondsToText(seconds)
            ids = self.get_users()
            msg = f"""

Hier is wat systeem informatie:
```
Bot versie: {version}
Database :  {dbsize}
Uptime :    {uptime}
Users :     {len(ids)}
```
"""

            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode='MarkdownV2')

        except Exception as e:
            log.error(e)

    def list_ids(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = self.dontunderstand_text
            if int(update.message.chat_id) in self.admin_ids:
                ids = self.get_users()
                msg = f"Here's the list of ids you requested!\n {str(ids)}"

            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)

    def onderhoud(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if int(update.message.chat_id) in self.admin_ids:
                if context.args[0] == 'aan':
                    msg = "We gaan even in ouderhoud voor updates! We zijn zo weer terug!"
                elif context.args[0] == 'uit':
                    msg = "Het onderhoud is gedaan. We zijn weer terug!"
                else:
                    msg = """
Ik begrijp je niet, het commando is
/onderhoud aan
/onderhoud uit
                    """
                    context.bot.send_message(chat_id=update.message.chat_id, text=msg)
                    return
                for id in self.get_users():
                    if id == 0:
                        continue
                    context.bot.send_message(chat_id=id, text=msg)

            else:
                context.bot.send_message(chat_id=update.message.chat_id, text=self.dontunderstand_text)
        except Exception as e:
            log.error(e)

    def fill_db(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if int(update.message.chat_id) in self.admin_ids:
                EP = EnergiePrijzen(dbname=self.dbname)
                EP.set_dates()

                context.bot.send_message(chat_id=update.message.chat_id, text=f"This is gonna take a while!!\n")

                #stroom vanaf 2017
                EP.get_history(startdate="2017-01-01", enddate="2017-01-02", kind=1)
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Energy import ready!!\n")
                #gas vanaf 2018
                EP.get_history(startdate="2018-01-01", enddate="2018-01-02", kind=2)
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Gas import ready!!\n")
                EP = None
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Databases filled!!\n")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text=self.dontunderstand_text)
        except Exception as e:
            log.error(e)

# some other functions
    @staticmethod
    def unitConvertor(sizeInBytes):
        try:
            #Cinverts the file unit
            if sizeInBytes < 1024*1024:
                size = round(sizeInBytes/1024)
                return f"{size} KB"
            elif sizeInBytes < 1024*1024*1024:
                size = round(sizeInBytes/(1024*1024))
                return f"{size} MB"
            elif sizeInBytes >= 1024*1024*1024:
                size = round(sizeInBytes/(1024*1024*1024))
                return f"{size} GB"
            else:
                return f"{sizeInBytes} Bytes"
        except Exception as e:
            log.error(e)

    def fileSize(self, filePath):
        try:
            size = os.path.getsize(filePath)
            return self.unitConvertor(size)
        except Exception as e:
            log.error(e)

    @staticmethod
    def secondsToText(unit, granularity = 2):
        try:
            ratios = {
                'decennia' : 311040000, # 60 * 60 * 24 * 30 * 12 * 10
                'jaar'   : 31104000,  # 60 * 60 * 24 * 30 * 12
                'maanden'  : 2592000,   # 60 * 60 * 24 * 30
                'dagen'    : 86400,     # 60 * 60 * 24
                'uur'   : 3600,      # 60 * 60
                'minuten' : 60,        # 60
                'seconden' : 1          # 1
            }

            texts = []
            for ratio in ratios:
                result, unit = divmod(unit, ratios[ratio])
                if result:
                    if result == 1:
                        ratio = ratio.rstrip('s')
                    texts.append(f'{result} {ratio}')
            texts = texts[:granularity]
            if not texts:
                return f'0 {list(ratios)[-1]}'
            text = ', '.join(texts)
            if len(texts) > 1:
                index = text.rfind(',')
                text = f'{text[:index]} and {text[index + 1:]}'
            return text
        except Exception as e:
            log.error(e)