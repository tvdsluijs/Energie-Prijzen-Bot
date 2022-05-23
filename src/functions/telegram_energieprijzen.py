import os
# import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler,CallbackQueryHandler
from functions.telegram_functions import Telegram_Functions
from telegram.ext.filters import Filters

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Telegram_EnergiePrijzen(Telegram_Functions):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def start_telegram(self)->None:
        try:
            u = Updater(self.telegram_key, use_context=True)
            j = u.job_queue

            # run every minute
            job_minute = j.run_repeating(self.call_energiebot, interval=60, first=1) #iedere minuut

            user_handler = CommandHandler(['u','user'], self.user)
            u.dispatcher.add_handler(user_handler)

            # admin handler
            admin_handler = CommandHandler(['a', 'admin'], self.admin)
            u.dispatcher.add_handler(admin_handler)

            u.dispatcher.add_handler(CallbackQueryHandler(self.button_press))

            prijs_handler = CommandHandler(['p','prijs', 'prijzen'], self.prijs)
            u.dispatcher.add_handler(prijs_handler)

            ochtend_handler = CommandHandler('ochtend', self.ochtend)
            u.dispatcher.add_handler(ochtend_handler)

            start_handler = CommandHandler('start', self.start_me_up)
            u.dispatcher.add_handler(start_handler)

            current_handler = CommandHandler('nu', self.get_current)
            u.dispatcher.add_handler(current_handler)

            today_handler = CommandHandler('vandaag', self.get_today)
            u.dispatcher.add_handler(today_handler)

            tomorrow_handler = CommandHandler('morgen', self.get_tomorrow)
            u.dispatcher.add_handler(tomorrow_handler)

            highprice_handler = CommandHandler('hoog', self.get_highprices)
            u.dispatcher.add_handler(highprice_handler)

            lowprice_handler = CommandHandler('laag', self.get_lowprices)
            u.dispatcher.add_handler(lowprice_handler)

            donate_handler = CommandHandler(['d','doneer'], self.donate)
            u.dispatcher.add_handler(donate_handler)

            system_handler = CommandHandler(['s', 'system', 'systeem'], self.systeminfo)
            u.dispatcher.add_handler(system_handler)

             # Help, Unknown handlers & enz
            commando_handler = CommandHandler(['c','commandos','commands'], self.commandos)
            u.dispatcher.add_handler(commando_handler)

            helpme_handler = CommandHandler(['h','help','hulp'], self.help_me)
            u.dispatcher.add_handler(helpme_handler)

            unknown_handler = MessageHandler(Filters.command, self.help_me)
            u.dispatcher.add_handler(unknown_handler)

            blahblah_handler = MessageHandler(Filters.text, self.help_me)
            u.dispatcher.add_handler(blahblah_handler)

            # Start the Bot
            u.start_polling()
            u.idle()
        except Exception as e:
            log.error(e)
            pass


if __name__ == "__main__":
    telegram_key = ""
    admin_ids = [2349539035,0]
    TE = Telegram_EnergiePrijzen(admin_ids=admin_ids,telegram_key=telegram_key)
    TE.start_telegram()
