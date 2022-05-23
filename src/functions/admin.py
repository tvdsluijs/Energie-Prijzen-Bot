import os
import logging

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import escape_markdown

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Admin():
    """Een class waarin alle Admin functies voor de bot staan."""
    def __init__(self, update:telegram.Update, context:telegram.ext.CallbackContext, user_ids:list = None, dbname:str=None) -> None:
        self.user_ids = user_ids
        self.context = context
        self.update = update

    def do_what(self, what:str = None) -> None:
        """Een functie die bepaald wat je wilt dat het doet /commando [watmoetikdoen] """
        try:
            what = self.context.args[0]
        except IndexError:
            pass

        if what is None:
            self.start()
            return

        try:
            match what:
                case "help":
                    return self.help()
                case "onderhoud":
                    return self.onderhoud()
                case "id_lijst":
                    return self.list_ids()
                case "vul_db":
                    return self.fill_db()
                case _:
                    return self.say_what()
                    pass
        except Exception as e:
            log.error(e)

    def start(self) -> int:
        try:
            keyboard = [
                [InlineKeyboardButton("Onderhoud aan", callback_data='onderhoud_aan')],
                [InlineKeyboardButton("Onderhoud uit", callback_data='onderhoud_uit')],
                [InlineKeyboardButton("ID's Lijstje", callback_data='id_list')],
                [InlineKeyboardButton("Database vullen", callback_data='vul_db')],
                [InlineKeyboardButton("Help", callback_data='help_admin')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message_reply_text = 'Hulp nodig bij je keuze?'
            self.update.message.reply_text(message_reply_text, reply_markup=reply_markup)

        except Exception as e:
            log.error(e)

    def say_what(self):
        """Een functie die geen idee heeft wat je wilt en dat ook laat weten"""
        try:
            msg = "Geen idee wat je bedoelt! Wil je hulp bij deze functie? /admin help"
            self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
            return True
        except Exception as e:
            log.error(e)
            return False

    def help(self, send_msg:int = 0, user_id:int = None):
        """Een functie die help tekst uitspuugt en verstuurd naar de gebruiker"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            msg =  """
Dit is de Admin help
/admin vul_db → vul de database met historische data
/admin id_lijst → lijst met aangemelde personen
/admin onderhoud aan → stuur iedereen een onderhoud bericht
/admin onderhoud uit → stuur iedereen een onderhoud bericht
/system → wat systeem informatie
/admin nexthourminus → is there a minus price next hour
/admin tomorrowminus → tomorrows 0 and below prices
/admin stuur_bericht → stuur bericht naar iedereeen
"""
            # 1 == return message, all other use bot
            if send_msg == 1:
                msg = escape_markdown(msg)
                return msg

            self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
            return True
        except Exception as e:
            log.error(e)
            return False

    def onderhoud(self, send_msg:int = 0, user_id:int = None, aan_uit:str = None):
        """Een functie waarmee je onderhoud aan of uit kan zetten"""
        """en een melding geeft naar alle gebruikers"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            try:
                aan_uit = self.context.args[1]
            except:
                pass

            if aan_uit is None:
                msg = """
Ik begrijp je niet, het commando is
/onderhoud aan
/onderhoud uit"""
                # 1 == return message, all other use bot
                if send_msg == 1:
                    return msg

                self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
                return msg

            match aan_uit:
                case 'aan':
                    msg = "We gaan even in ouderhoud voor updates! We zijn zo weer terug!"
                case 'uit':
                    msg = "Het onderhoud is gedaan. We zijn weer terug!"

            for id in self.user_ids:
                if id == 0:
                    continue
                self.context.bot.send_message(chat_id=id, text=msg)

            return True
        except Exception as e:
            log.error(e)
            return False

    def fill_db(self, send_msg:int = 0, user_id:int = None):
        """Een functie waarmee je de database kan vullen met historische data"""
        """Deze functie staat even uit"""
        # TODO: herschrijven functie

        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            self.context.bot.send_message(chat_id=self.update.message.chat_id, text=f"Deze is ff stuk")
        #     EP = EnergiePrijzen(dbname=self.dbname)
        #     EP.set_dates()

        #     self.context.bot.send_message(chat_id=self.update.message.chat_id, text=f"This is gonna take a while!!\n")

        #     #stroom vanaf 2017
        #     EP.get_history(startdate="2017-01-01", enddate="2017-01-02", kind=1)
        #     self.context.bot.send_message(chat_id=self.update.message.chat_id, text=f"Energy import ready!!\n")
        #     #gas vanaf 2018
        #     EP.get_history(startdate="2018-01-01", enddate="2018-01-02", kind=2)
        #     self.context.bot.send_message(chat_id=self.update.message.chat_id, text=f"Gas import ready!!\n")
        #     EP = None
        #     self.context.bot.send_message(chat_id=self.update.message.chat_id, text=f"Databases filled!!\n")
            msg = "Deze functie is offline!"
            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            return True
        except Exception as e:
            log.error(e)
            return False

    def stuur_bericht(self, send_msg:int = 0, user_id:int = None):
        """Een functie waarmee je alle gebruikers een bericht kan sturen database kan vullen met historische data"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            try:
                if not self.context.args:
                    raise IndexError
                msg =' '.join(self.context.args)
            except IndexError:
                msg = """
Ik begrijp je niet, het commando is
/send_message 'Hallo dit is een bericht'"""
            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

                self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
                return

            for id in self.user_ids:
                if id == 0:
                    continue
                self.context.bot.send_message(chat_id=id, text=msg)

            # 1 == return message, all other use bot
            if send_msg == 1:
                return "Berichten zijn verstuurd!"


            return True
        except Exception as e:
            log.error(e)
            return False

    def list_ids(self, send_msg:int = 0, user_id:int = None):
        """Een functie waarmee je een lijstje krijgt van alle gebruikers_ids"""
        """Het systeem slaat alleen ID's op en verder geen privacy gevoelige info"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            msg = f"Hier is een lijst met ID's \n {str(self.user_ids)}"

            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
            return True
        except Exception as e:
            log.error(e)
            return False