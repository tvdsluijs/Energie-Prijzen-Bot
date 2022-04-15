from ast import Constant
import os
import sys
import telegram
from telegram.ext import Updater, CommandHandler
from functions.energieprijzen import EnergiePrijzen
from functions.energieprijzen_sql import EnergiePrijzen_SQL

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Telegram_Functions(object):
    ENERGIE = Constant(1)
    GAS = Constant(2)

    def __init__(self, *args, **kwargs) -> None:
        try:
            self.dbname = 'energieprijzen.db'
            self.telegram_key = kwargs['telegram_key']
            self.admin_id = kwargs['admin_id']

            self.help_tekst = """
Let op! Alle energie bedragen zijn de kale inkoopsprijzen.
Dus zonder opslag, BTW en belastingen.

Er zijn de volgende commando's tot je beschikking

/voegmetoe -> voegt je chat-ID toe
/verwijderme -> verwijdert je chat-ID
/mijnid -> toont je chat-ID
/nu -> toont huidige prijzen
/vandaag -> toont de prijzen van vandaag
/morgen -> toont u de prijzen van morgen (na 15.00 uur)
/laag -> toont de laagste prijzen van vandaag
/hoog -> toont de hoogste prijzen van vandaag

Als je een /voegmetoe doet, ontvang je:
- dagelijks rond 15:00 uur de laagste prijzen voor morgen;
- voordat de laagste prijs van de dag begint een bericht;
- informatie over prijzen onder 0.

Vergeet niet te doneren!!
/doneer

Vragen? Mail naar info@itheo.tech
"""

            super().__init__()
        except KeyError as e:
            log.error(e)
        except Exception as e:
            log.critical(e)

    def start_me_up(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            help_text = """Welkom bij de Energie prijzen bot!\n""" + self.help_tekst

            context.bot.send_message(chat_id=update.message.chat_id, text=help_text)
        except Exception as e:
            log.error(e)


    def help_me(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            help_text = """Ik ben hier om je te helpen!\n""" + self.help_tekst

            context.bot.send_message(chat_id=update.message.chat_id, text=help_text)
        except Exception as e:
            log.error(e)


    def donate(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            context.bot.send_message(chat_id=update.message.chat_id, text="https://donorbox.org/tvdsluijs-github")
        except Exception as e:
            log.error(e)

    def call_energiebot(self, context: telegram.ext.CallbackContext):
        try:
            #update prices
            #at 16hour do a send lowest prices overview
            #every hour send a at next hour you will have the lowest prices
            EP = EnergiePrijzen()
            EP.set_dates()

            #stroom = 1, gas 2 2
            for sg in [1,2]:
                data = EP.get_energyzero_data(kind=sg)
                EP.save_data(data=data, kind=sg)

            if int(EP.current_hour_short) not in [23,0,1,2,3,4,5,6]:
                ids = self.get_users()
                if (msg := EP.get_next_hour_lowest_price()):
                    for id in ids:
                        if id == 0:
                            continue
                        context.bot.send_message(chat_id=id, text=msg)

                if (msg := EP.get_next_hour_minus_price()):
                    for id in ids:
                        if id == 0:
                            continue
                        context.bot.send_message(chat_id=id, text=msg)

                if (msg := EP.get_tomorrows_minus_price()):
                    for id in ids:
                        if id == 0:
                            continue
                        context.bot.send_message(chat_id=id, text=msg)

            #NOG IETS?
            #Tomorrows prices
            EP = None
        except Exception as e:
            log.error(e)

    def get_users(self)->list:
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            ids = []
            ids = esql.get_users()
            ids.append(0)
            esql = None
            return ids
        except Exception as e:
            log.error(e)

    def list_ids(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if int(update.message.chat_id) == int(self.admin_id):
                ids = self.get_users()
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Here's the list of ids you requested!\n {str(ids)}")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I'm not allowed to show you!")
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
            msg = "Sorry, ik heb je niet begrepen, zocht je naar /hulp ?"
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
                    mss = f"Jouw user chat id ({update.message.chat_id}) staat al in het systeem!"
                case 1:
                    mss = f"Ik heb je toegevoegd met user chat id: {update.message.chat_id}! Vanaf nu ontvang je de energie prijzen!"
                case -1:
                    mss = f"Ai... we hebben een probleem om je toe te voegen met user chat id ({update.message.chat_id}). Probeer het nog een keer of stuur een mail naar info@itheo.tech als dit probleem blijft."

            context.bot.send_message(chat_id=update.message.chat_id, text=mss)
        except Exception as e:
            log.error(e)

    def remove_me(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            mss_id = esql.remove_user(user_id=update.message.chat_id)
            esql = None
            mss = "Oeps... er ging iets fout!"

            print(mss_id)

            match mss_id:
                case 0:
                    mss = f"Jouw user chat id ({update.message.chat_id}) is niet gevonden, dus verwijderen kan niet!"
                case 1:
                    mss = f"Jouw user chat id ({update.message.chat_id}) is verwijdert! Je ontvangt nu geen energie prijzen meer!"
                case -1:
                    mss = f"Ai... we hebben een probleem om jouw user chat id ({update.message.chat_id}) te verwijderen. Probeer het nog een keer of stuur een mail naar info@itheo.tech als dit probleem blijft."

            context.bot.send_message(chat_id=update.message.chat_id, text=mss)
        except Exception as e:
            log.error(e)

    def get_id(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            context.bot.send_message(chat_id=update.message.chat_id, text=f"Jouw user chat id is {update.message.chat_id}!")
        except Exception as e:
            log.error(e)

    def get_today(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen()
            EP.set_dates()
            message = EP.get_todays_prices(date=EP.today)
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        except Exception as e:
            log.error(e)

    def get_tomorrow(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen()
            EP.set_dates()
            if int(EP.current_hour_short) < 15:
                message = "Sorry, het is nog geen 15uur geweest!"
            else:
                message = EP.get_todays_prices(date=EP.enddate)
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        except Exception as e:
            log.error(e)

    def fill_db(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if int(update.message.chat_id) == int(self.admin_id):
                EP = EnergiePrijzen()
                EP.set_dates()
                #stroom vanaf 2017
                EP.get_history(startdate="2017-01-01", enddate="2017-01-02", kind=1)
                #gas vanaf 2018
                EP.get_history(startdate="2018-01-01", enddate="2018-01-02", kind=2)
                EP = None
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Databases filled!!\n")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I'm not allowed to show you!")
        except Exception as e:
            log.error(e)

    def get_current(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen()
            EP.set_dates()
            message = EP.get_cur_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        except Exception as e:
            log.error(e)

    def get_highprices(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen()
            EP.set_dates()
            message = EP.get_todays_highest_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        except Exception as e:
            log.error(e)

    def get_lowprices(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen()
            EP.set_dates()
            message = EP.get_todays_lowest_price()
            EP = None
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        except Exception as e:
            log.error(e)