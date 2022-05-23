import os
import logging

# import telegram

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Help():
    """Een  class waarin alle help functionaliteiten voor de bot staan."""
    def __init__(self) -> None:
        pass

    # def do_what(self, what:str = None):
    #     """Een functie die bepaald wat je wilt, /commando wat """
    #     try:
    #         what = self.context.args[0]
    #     except IndexError():
    #         return False

    #     try:
    #         match what:
    #             case "help":
    #                 self.help_help()
    #             case _:
    #                 self.say_what()
    #                 pass
    #     except Exception as e:
    #         log.error(e)

    # def help_help(self)->bool:
    #     """Klein grapje wanneer iemand help over help vraagt"""
    #     try:
    #         msg = "Vraag je nou echt om hulp over help?"
    #         self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
    #         return True
    #     except Exception as e:
    #         log.error(e)
    #         return False

    # def say_what(self)->bool:
    #     """Een functie die geen idee heeft wat je wilt en dat ook laat weten"""
    #     try:
    #         msg = "Geen idee wat je bedoelt wil je hulp bij deze functie? /help help"
    #         self.context.bot.send_message(chat_id=self.update.message.chat_id, text=msg)
    #         return True
    #     except Exception as e:
    #         log.error(e)
    #         return False

    @staticmethod
    def foutmelding(fout:str = "")->str:
        try:
            return f"🚧 Great Scott 🚧 \n Je bent tegen een fout aangelopen.\n {fout}"
        except Exception as e:
            log.error(e)

    @staticmethod
    def dontunderstand()->str:
        try:
            return """Sorry, ik heb je niet begrepen. Ben je opzoek naar /hulp?"""
        except Exception as e:
            log.error(e)

    @staticmethod
    def help()->str:
        try:
            return """
Let op: alle bedragen zijn kale inkoopprijzen, dus zonder opslag, BTW en belastingen

Voor overzicht van alle /commands

/voegmetoe voor automatische berichten:
- de laagste prijzen van morgen;
- bericht voordat laagste prijs begint;
- informatie over prijzen onder 0

Vergeet niet te doneren
/doneer

Vragen?
Mail naar info@itheo.tech
"""
        except Exception as e:
            log.error(e)


    @staticmethod
    def say_what():
        try:
            return "Geen idee wat je bedoelt"
        except Exception as e:
            log.error(e)