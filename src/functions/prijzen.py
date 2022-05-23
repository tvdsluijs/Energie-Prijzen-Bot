import os
import logging

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Prijzen:
    def __init__(self, update:telegram.Update, context:telegram.ext.CallbackContext, user_ids:list = None) -> None:
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
                case "nu":
                    return self.nu()
                case "laag":
                    return self.laag()
                case "hoog":
                    return self.hoog()
                case "morgen":
                    return self.morgen()
                case _:
                    return self.say_what()
                    pass
        except Exception as e:
            log.error(e)

    def start(self) -> int:
        try:
            keyboard = [
                [InlineKeyboardButton("Prijzen Nu", callback_data='prijzen_nu')],
                [InlineKeyboardButton("Prijzen morgen", callback_data='prijzen_morgen')],
                [InlineKeyboardButton("Prijzen laag", callback_data='prijzen_laag')],
                [InlineKeyboardButton("Prijzen hoog", callback_data='prijzen_hoog')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message_reply_text = 'Hulp nodig bij je keuze?'
            self.update.message.reply_text(message_reply_text, reply_markup=reply_markup)

        except Exception as e:
            log.error(e)

    def help(self, send_msg:int = 0, user_id:int = None):
        """Een functie die help tekst uitspuugt en verstuurd naar de gebruiker"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            msg =  """
Dit is de Prijzen help
/p nu → Huidige prijzen
/p laag → laagste vandaag
/p hoog → hoogste vandaag
/p morgen → prijzen van morgen, na 15u
            """
            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
            return True
        except Exception as e:
            log.error(e)
            return False

    def nu()->str:
        pass

    def ochtend()->str:
        pass

    def middag()->str:
        pass

    def laag()->str:
        pass

    def hoog()->str:
        pass

    def morgen()->str:
        pass