import sys
import os
from time import time

import configparser
import logging
import logging.config

from functions.telegram_energieprijzen import Telegram_EnergiePrijzen
from functions.energieprijzen_sql import EnergiePrijzen_SQL
from functions.energieprijzen import EnergiePrijzen

os.environ['TZ'] = 'Europe/Amsterdam'

dir_path = os.path.dirname(os.path.realpath(__file__))
log_folder = os.path.join(dir_path, 'logging')
config_folder = os.path.join(dir_path, 'config')

os.makedirs(log_folder, exist_ok=True)

logging.config.fileConfig(os.path.join(config_folder, 'logging.conf'))

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

if PY_ENV == 'prod':
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

class EnergieBot():
    def __init__(self) -> None:
        try:
            self.config_file = os.path.join(config_folder, 'config.conf')
            if not self.check_file(file=self.config_file):
                raise Exception('Config file not found')
            self.config = None
            self.admin_ids = None
            self.telegram_key = None
            self.initConfig()
            self.readConfig()
        except Exception as e:
            log.critical(e)
            sys.exit(e)

    @staticmethod
    def check_file(file:str = "")->bool:
        if os.path.exists(file):
            return True
        return False

    def initConfig(self) -> None:
        try:
            self.config = configparser.ConfigParser()
            self.config.read(self.config_file)
        except Exception as e:
            log.critical(e)
            sys.exit(e)

    def readConfig(self)-> None:
        try:
            admin_ids = self.config['telegram']['admin_ids'].split(',')
            self.admin_ids = [int(i) for i in admin_ids]
            self.telegram_key = self.config['telegram']['key']
        except KeyError as e:
            log.critical(e)
        except Exception as e:
            log.error(e)
            sys.exit(e)


if __name__ == "__main__":
    startTime = time()
    eb = EnergieBot()
    dbname = "data/energieprijzen.db"
    esql = EnergiePrijzen_SQL(dbname=dbname)
    for table in ['energy', 'user']:
        esql.no_table(table=table)
    if eb.admin_ids:
        for id in eb.admin_ids:
            if int(id) == 0:
                continue
            esql.add_user(user_id=int(id))
    esql = None
    path = os.path.dirname(os.path.realpath(__file__))
    TE = Telegram_EnergiePrijzen(dbname=dbname,admin_ids=eb.admin_ids,telegram_key=eb.telegram_key, path=path, startTime=startTime)
    TE.start_telegram()
