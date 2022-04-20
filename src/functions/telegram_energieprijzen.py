import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
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

            # run every hour
            job_minute = j.run_repeating(self.call_energiebot, interval=3600, first=2) #ieder uur!

            get_id_handler = CommandHandler('mijnid',self.get_id)
            u.dispatcher.add_handler(get_id_handler)

            addme_handler = CommandHandler('voegmetoe', self.add_me)
            u.dispatcher.add_handler(addme_handler)

            removeme_handler = CommandHandler('verwijderme', self.remove_me)
            u.dispatcher.add_handler(removeme_handler)

            listids_handler = CommandHandler('listids', self.list_ids)
            u.dispatcher.add_handler(listids_handler)

            start_handler = CommandHandler('start', self.start_me_up)
            u.dispatcher.add_handler(start_handler)

            helpme_handler = CommandHandler('help', self.help_me)
            u.dispatcher.add_handler(helpme_handler)

            hulpme_handler = CommandHandler('hulp', self.help_me)
            u.dispatcher.add_handler(hulpme_handler)

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

            donate_handler = CommandHandler('doneer', self.donate)
            u.dispatcher.add_handler(donate_handler)

            # admin handlers
            filldb_handler = CommandHandler('fill', self.fill_db)
            u.dispatcher.add_handler(filldb_handler)

            system_handler = CommandHandler('system', self.systeminfo)
            u.dispatcher.add_handler(system_handler)

            onderhoud_handler = CommandHandler('onderhoud', self.onderhoud)
            u.dispatcher.add_handler(onderhoud_handler)

            # Unknown handlers

            unknown_handler = MessageHandler(Filters.command, self.dontunderstand)
            u.dispatcher.add_handler(unknown_handler)

            blahblah_handler = MessageHandler(Filters.text, self.blahblah)
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
