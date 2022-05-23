import os,sys
from time import time
from datetime import datetime, timedelta

from ast import Constant

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.utils.helpers import escape_markdown

from functions.energieprijzen import EnergiePrijzen
from functions.energieprijzen_sql import EnergiePrijzen_SQL

from functions.admin import Admin
from functions.commandos import Commandos
from functions.help import Help

import logging
from functions.systeem import Systeem

from functions.user import User


PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)

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
            self.entsoe_key = kwargs['entsoe_key']

            self.date_hours = []

            H = Help()
            self.help_tekst = H.help()
            self.dontunderstand_text = H.dontunderstand()
            self.foutmelding = H.foutmelding()

            C = Commandos()
            self.commands = C.commands()
            self.admin_commands = C.all_commands()

            super().__init__()
        except KeyError as e:
            log.error(e)
        except Exception as e:
            log.critical(e)

    def admin(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            if int(update.message.chat_id) in self.admin_ids:
                Adm = Admin(update=update, context=context, user_ids=self.get_users())
                Adm.do_what(what=None)
            else:
                raise IndexError
        except IndexError as e:
            context.bot.send_message(chat_id=update.message.chat_id, text=self.dontunderstand_text)
        except Exception as e:
            log.error(e)

    def prijs(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            print('hello')
            pass
        except Exception as e:
            log.error(e)


    def user(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            U = User(update=update, context=context, dbname=self.dbname)
            U.do_what()
        except Exception as e:
            log.error(e)

    def button_press(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        try:
            """Parses the CallbackQuery and updates the message text."""
            query = update.callback_query
            query.answer()
            user_id = query['message']['chat']['id']
            print(query.data)

            match query.data:
                case 'user_get_id':
                    U = User(update=update, context=context, dbname=self.dbname)
                    msg = U.get_id(send_msg=1, user_id=user_id)
                case 'user_instellingen':
                    U = User(update=update, context=context, dbname=self.dbname)
                    msg = U.mijn_instellingen(send_msg=1, user_id=user_id)
                case 'sure_delete':
                    U = User(update=update, context=context, dbname=self.dbname)
                    U.sure_delete(user_id=user_id)
                    query.edit_message_text(text=" ")
                case 'verwijder_user':
                    U = User(update=update, context=context, dbname=self.dbname)
                    msg = U.delete_me(send_msg=1, user_id=user_id)
                case 'user_help':
                    U = User(update=update, context=context, dbname=self.dbname)
                    msg = U.help(send_msg=1, user_id=user_id)
                case 'nee':
                    msg = "Okay, dan niet\!"
                case 'help_admin':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    msg = A.help(send_msg=1, user_id=user_id)
                case 'onderhoud_aan':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    # msg = A.list_ids(send_msg=1, user_id=user_id)
                case 'onderhoud_uit':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    # msg = A.list_ids(send_msg=1, user_id=user_id)
                case 'onderhoud_aan':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    # msg = A.list_ids(send_msg=1, user_id=user_id)
                case 'id_list':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    msg = A.list_ids(send_msg=1, user_id=user_id)
                case 'vul_db':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    msg = A.fill_db(send_msg=1, user_id=user_id)
                case 'admin_help':
                    A = Admin(update=update, context=context, dbname=self.dbname)
                    msg = A.help(send_msg=1, user_id=user_id)
                    pass
                case _:
                    print(query.data)

            if msg == "":
                msg = self.dontunderstand_text
                # msg = escape_markdown(msg, version=2)
            query.edit_message_text(text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def start_me_up(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            first_name = update.message.chat.first_name
            username = update.message.chat.username

            if first_name is None or first_name == "":
                name = username
            else:
                name = first_name

            msg = f"""Hoi {name}, welkom bij de Energie prijzen bot
{self.help_tekst}
"""
            msg = escape_markdown(msg, version=2)
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def help_me(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            first_name = update.message.chat.first_name
            username = update.message.chat.username

            if first_name is None or first_name == "":
                name = username
            else:
                name = first_name

            msg = f"""Hoi {name},
ik ben hier om je te helpen
{self.help_tekst}
"""
            msg = escape_markdown(msg, version=2)
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def commandos(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = escape_markdown(self.commands, version=2)
            if int(update.message.chat_id) in self.admin_ids:
                msg = escape_markdown(self.admin_commands, version=2)

            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
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

            # Check if current hour in , if so do not run!
            if date_hour in self.date_hours:
                return

            # hour not in list so do somehtings
            self.date_hours.append(date_hour) # add hour to list
            self.date_hours = self.date_hours[-5:] # remove last hour

            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            cur_hour = int(now.strftime("%H"))

            #stroom = 1, gas = 2
            # Gas ophalen bij ernergyzero
            if (data := EP.get_energyzero_data(kind=2)):
                EP.save_data(data=data, kind=2)

            # Electra ophalen bij entsoe
            if (data := EP.get_entsoe_data(entsoe_key=self.entsoe_key)):
                EP.save_data(data=data, kind=1)
            #wanneer er geen data is dan bij energyzero ophalen.
            elif (data := EP.get_energyzero_data(kind=1)):
                EP.save_data(data=data, kind=1)

            ochtend_ids = EP.get_ochtend_users(cur_hour)
            if ochtend_ids:
                if (msg := EP.ochtend_message()):
                    for id in ochtend_ids:
                        if id == 0:
                            continue
                        context.bot.send_message(chat_id=id, text=msg)

            if cur_hour not in [23,0,1,2,3,4,5,6]:
                ids = self.get_users()

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
                            context.bot.send_message(chat_id=id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
            del EP
        except Exception as e:
            log.error(e)

    def get_users(self) -> list:
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            ids = []
            ids = esql.get_users()
            ids.append(0)
            del esql
            return ids
        except Exception as e:
            log.error(e)


    def ochtend(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            msg = ""
            esql = EnergiePrijzen_SQL(dbname=self.dbname)

            if context.args[0] == 'aan':
                tijd = context.args[1]
                if esql.update_ochtend(user_id=update.message.chat_id, tijd=tijd):
                    msg = f"Ochtend melding staat aan om {tijd} uur"
                else:
                    msg = self.foutmelding

            elif context.args[0] == 'uit':
                if esql.update_ochtend(user_id=update.message.chat_id, tijd=None):
                    msg = f"Ochtend melding staat uit"
                else:
                    msg = self.foutmelding
            if msg == "":
                msg = """Sorry, dit commando moet uitgevoerd worden als volgt:

/ochtend aan 9
Hiermee zet je de ochtend melding aan om 9 uur

Je kan de ochtend melding aanpassen door bijvoorbeeld:
/ochtend aan 10

/ochtend uit
Hiermee zet je de ochtend melding uit
"""
            del esql
            context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        except Exception as e:
            log.error(e)


    def get_today(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_todays_prices(date=EP.today)
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def get_tomorrow(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            if int(EP.current_hour_short) < 15:
                msg = """Prijzen van morgen zijn pas na 15u beschikbaar"""
            else:
                msg = EP.get_todays_prices(date=EP.tomorrow)
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def get_current(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_cur_price()
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def get_highprices(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_todays_highest_price()
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def get_lowprices(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_todays_lowest_price()
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    # some admin functions

    def tomorrowminus(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_tomorrows_minus_price()
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def nexthourminus(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            msg = EP.get_next_hour_lowest_price()
            del EP
            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)

    def systeminfo(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        try:
            versie_path = os.path.join(self.path, "VERSION.TXT")
            version = open(versie_path, "r").read().replace('\n','')
            seconds = int(time() - self.startTime)

            EP = EnergiePrijzen(dbname=self.dbname)
            EP.set_dates()
            dt = EP.current_date_time
            del EP
            users = len(self.get_users())
            S = Systeem()

            msg = S.systeminfo_msg(dt=dt, version=version, users=users, seconds=seconds, dbname=self.dbname)
            del S

            context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)

        except Exception as e:
            log.error(e)