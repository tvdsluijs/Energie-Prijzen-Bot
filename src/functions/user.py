import os
import logging

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.utils.helpers import escape_markdown
from functions.energieprijzen_sql import EnergiePrijzen_SQL

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class User:
    """Een class met alle user functies er in"""
    def __init__(self, update:telegram.Update, context:telegram.ext.CallbackContext, dbname:str=None) -> None:
        self.dbname = dbname
        self.context = context
        self.update = update

    def do_what(self, what:str = None) -> None:
        """Een functie die bepaald wat je wilt dat het doet /commando [watmoetikdoen]"""
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
                case "verwijder":
                    return self.delete_me()
                case "id":
                    return self.get_id()
                case "instellingen":
                    return self.mijn_instellingen()
                case _:
                    return self.say_what()
                    pass
        except Exception as e:
            log.error(e)

    def start(self) -> int:
        try:
            keyboard = [
                [InlineKeyboardButton("Toon Chat ID", callback_data='user_get_id')],
                [InlineKeyboardButton("Toon instellingen", callback_data='user_instellingen')],
                [InlineKeyboardButton("Verwijder me", callback_data='sure_delete')],
                [InlineKeyboardButton("Toon User help", callback_data='user_help')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message_reply_text = 'Hulp nodig bij je keuze?'
            self.update.message.reply_text(message_reply_text, reply_markup=reply_markup)

        except Exception as e:
            log.error(e)

    def sure_delete(self, user_id:int = None) -> int:
        try:
            keyboard = [
                [InlineKeyboardButton("Ja, verwijder me!", callback_data='verwijder_user')],
                [InlineKeyboardButton("Nee, tock niet!", callback_data='nee')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message_reply_text = 'Weet je het zeker?'

            self.context.bot.send_message(chat_id=user_id, text=message_reply_text, reply_markup=reply_markup)

        except Exception as e:
            log.error(e)

    def say_what(self):
        """Een functie die geen idee heeft wat je wilt en dat ook laat weten"""
        try:
            msg = "Geen idee wat je bedoelt! Wil je hulp bij deze functie? /user help"
            self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
            return True
        except Exception as e:
            log.error(e)
            return False

    def mijn_instellingen(self, send_msg:int = 0, user_id:int = None)->bool:
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            user = esql.get_user(user_id=user_id)
            inst = ''

            if not user and not user['user_id']:
                return "Sorry we kunnen je niet vinden in het systeem\!"
            else:
                inst += f"""
Opgeslagen chat id: {user['user_id']}
"""
                dag_tijd =  user['datetime']
                inst += f"""Aangemeld sinds: {dag_tijd}
"""
                if user['ochtend'] is not None and user['ochtend']  != '':
                    inst += f"""Ochtend melding: aan {user['ochtend']}u
"""
                else:
                    inst += """Ochtend melding: uit
"""

                if user['middag'] is not None and user['middag'] != '':
                    inst += f"""Middag melding: aan
"""
                else:
                    inst += """Middag melding: uit
"""

                match user['kaal_opslag_allin']:
                    case 0:
                        inst += f"""Prijzen: Kale inkoop
"""
                    case 1:
                        inst += f"""Prijzen: Opslag & BTW
"""
                    case 2:
                        inst += f"""Prijzen: All-In
"""
                    case _:
                        pass

                if user['opslag'] is not None and user['opslag'] != '':
                        inst += f"""Prijs opslag: € {user['opslag']}
"""

                if user['melding_lager_dan'] is not None and user['melding_lager_dan'] != '':
                    inst += f"""Melding bij lager dan: {user['melding_lager_dan']}
"""
                else:
                    inst += "Melding bij lager dan: uit"

                if user['melding_hoger_dan'] is not None and user['melding_hoger_dan'] != '':
                    inst += f"""Melding bij hoger dan: {user['melding_hoger_dan']}
"""
                else:
                    inst += "Melding bij hoger dan: uit"

                msg = f"""
Jouw huidige instellingen:
```
{inst}
```
"""
            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            # msg = escape_markdown(msg, version=2)
            self.context.bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e:
            log.error(e)
            return False

    def get_id(self,send_msg:int = 0, user_id:int = None)->bool:
        """Functie om gebruiker / chat id mee te tonen"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            msg = f"Jouw user chat id is {user_id}\!"

            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            self.context.bot.send_message(chat_id=user_id, text=msg)
            return True
        except Exception as e:
            log.error(e)
            return False

    def delete_me(self, send_msg:int = 0, user_id:int = None)->bool:
        """Functie om gebruiker mee te verwijderen uit het systeem"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            user = esql.get_user(user_id=user_id)

            msg = f"We hebben een probleem om jouw gegevens met chat id ({user_id}) te verwijderen, probeer het nog een keer of stuur een mail naar info@itheo\.tech als dit probleem blijft"
            if user['user_id'] is None:
                msg = f"Jouw user chat id ({user_id}) is niet gevonden, dus je gegevens verwijderen kan niet"
            else:
                if esql.remove_user(user_id=user_id):
                    msg = f"Jouw gegevens met user id ({user_id}) zijn verwijdert\! Je ontvangt nu geen automatische energie updates"

            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            self.context.bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            log.error(e)
        finally:
            esql = None

    def help(self, send_msg:int = 0, user_id:int = None):
        """Een functie die help tekst uitspuugt en verstuurd naar de gebruiker"""
        try:
            if user_id is None:
                user_id = self.update.message.chat_id

            msg = """
Dit is de User help

/user verwijder → je gegevens verwijderen
/user id  → je chat id inzien
/user instellingen → instellingen"""

            # 1 == return message, all other use bot
            if send_msg == 1:
                return msg

            self.context.bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            log.error(e)
