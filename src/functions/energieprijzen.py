from ast import Constant
import os
import json
import requests
import logging

from datetime import datetime, timedelta
from dateutil import parser, tz

from time import sleep
from functions.energieprijzen_sql import EnergiePrijzen_SQL

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

class EnergiePrijzen():
    ENERGIE = Constant(1)
    GAS = Constant(2)

    def __init__(self, dbname:str = None) -> None:
        if dbname is None:
            raise Exception("No dbname in EnergiePrijzen")

        self.dbname = dbname
        self.now = None
        self.yesterday = None
        self.tomorrow = None
        self.dayaftertomorrow = None
        self.startdate = None
        self.enddate = None
        self.current_hour = None
        self.next_hour = None
        self.lowest_electricity = None
        self.highest_electricity = None
        self.lowest_time = None
        self.current_hour_short = None
        self.prices = {}

        self.weekdays = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
        self.months = ['', 'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']
        self.nice_day = None #net uitgeschreven dag donderdag 22 april

    @staticmethod
    def get_timestamp(time_stamp:str = "")->dict:
        try:
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('CET')

            d = parser.parse(time_stamp)

            utc = d.replace(tzinfo=from_zone)
            cet = utc.astimezone(to_zone)

            datum = cet.strftime('%Y-%m-%d')  #==> '1975-05-14'
            tijd = cet.strftime('%H:00')  #==> '18:00'

            return {'datum': datum, 'tijd': tijd}
        except Exception as e:
           log.error(e)

    def set_dates(self)->None:
        try:
            self.now = datetime.now()
            self.yesterday = datetime.now() + timedelta(days=-1)
            self.tomorrow = datetime.now() + timedelta(days=+1)

            self.today = self.now.strftime("%Y-%m-%d")
            self.startdate = self.yesterday.strftime("%Y-%m-%d")
            self.enddate = self.tomorrow.strftime("%Y-%m-%d")

            self.current_hour = self.now.strftime("%H:00")
            self.current_hour_short = int(self.now.strftime("%H"))

            self.next_hour = datetime.now() + timedelta(hours=+1)
            self.next_hour = self.next_hour.strftime("%H:00")

        except Exception as e:
            log.error(e)

    @staticmethod
    def get_next_hour(hours:int = 1):
        next_hour = datetime.now() + timedelta(hours=+hours)
        return next_hour.strftime("%H:00")

    def get_energyzero_data(self, startdate:str = "", enddate:str = "",kind:str = ENERGIE.value)->json:
        try:
            if startdate == "":
                startdate = self.startdate
            if enddate == "":
                enddate = self.enddate
            # interval=4 => dag
            # interval=9 => Week
            # interval=5 => Maand
            # interval=6 => Jaar
            url = f"https://api.energyzero.nl/v1/energyprices?fromDate={startdate}T00%3A00%3A00.000Z&tillDate={enddate}T23%3A59%3A59.999Z&interval=4&usageType={kind}&inclBtw=false"
            response = requests.get(url)
            data = response.json()
            if not data['Prices']:
                raise Exception('We did not get data from energyzero api')
            return data
        except KeyError as e:
            log.warning(f"We did not get data from energyzero api : {e}")
        except Exception as e:
            log.error(e)

    def get_history(self, startdate:str = "2017-01-01", enddate:str = "2017-01-02", kind:int = 1)->None:
        try:
            now = datetime.now()
            start = datetime.strptime(startdate, "%Y-%m-%d")

            while start <= now:
                # Get data
                data = self.get_energyzero_data(startdate=startdate,enddate=enddate, kind=kind)
                # Save data
                self.save_data(data=data, kind=kind)

                # new start end date
                start = datetime.strptime(startdate, "%Y-%m-%d")
                end = datetime.strptime(enddate, "%Y-%m-%d")

                next_start = start + timedelta(days=+1)
                next_end = end + timedelta(days=+1)

                startdate = next_start.strftime("%Y-%m-%d")
                enddate = next_end.strftime("%Y-%m-%d")
                sleep(2)
        except Exception as e:
            log.error(e)

    def save_data(self, data:dict = None, kind:int = None)->bool:
        try:
            if data is None:
                raise Exception('No data to save!')
            if kind is None:
                raise Exception('No power kind!')

            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            esql.connection()

            str_kind = ""
            match kind:
                case self.GAS.value:
                    str_kind = 'g'
                case self.ENERGIE.value:
                    str_kind = 'e'
                case _:
                    raise Exception('No correct power kind!')

            for row in data['Prices']:
                prices = {}
                efrom = self.get_timestamp(row['readingDate'])
                prices['fromdate'] = efrom['datum']
                prices['fromtime'] = efrom['tijd']
                prices['price'] =  row['price']
                prices['kind'] = str_kind
                esql.add_price(**prices)

        except Exception as e:
            log.error(e)
        finally:
            esql.close()

    def get_negative_price(self, date:str = None)->str:
        try:
            if date is None:
                date = self.now.strftime("%Y-%m-%d")
            esql = EnergiePrijzen_SQL(dbname=self.dbname)

        except Exception as e:
            log.error(e)
        finally:
            esql.close()

    def get_prices(self, date:str=None, kind:str = None)->dict:
        try:
            if date is None:
                date = self.now.strftime("%Y-%m-%d")

            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            return esql.get_prices(date=date, kind=kind)
        except Exception as e:
            log.error(e)
        finally:
            esql.close()

    def get_next_hour_minus_price(self, date:str = None)->str:
        try:
            if date is None:
                date = self.today
            data = self.get_prices(date=date, kind='e')
            msg = ""
            if data is not None:
                for d in data:
                    if d['fromtime'] == self.next_hour and d['price'] <= 0:
                        msg = f"Om {d['fromtime']} gaat de ⚡ prijs naar\n"
                        msg += f"""€ {d['price']:.2f}\n"""
            if msg != "":
                return msg
            return False
        except KeyError as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"

    def get_next_hour_lowest_price(self, date:str = None)->str:
        try:
            if date is None:
                date = self.today
            data = self.get_lowest_price(date=date)
            msg = ""
            prijs = 0
            nexthour = ""
            tottijd = None
            if data['elect'] is not None:
                msg = f"Laagste prijs van {self.get_nice_day(date=date)}"
                h = 1
                for d in data['elect']:

                    if d['fromtime'] == self.next_hour:
                        vantijd = d['fromtime']
                        prijs = d['prijs']
                        continue

                    nexthour = self.get_next_hour(hours=h)
                    h += 1
                    if prijs == d['prijs'] and d['fromtime'] == nexthour:
                        tottijd = self.get_next_hour(hours=h)

                if tottijd is not None:
                     msg += f""" tussen {vantijd} en {tottijd}\n ⚡  € {prijs} \n"""
                else:
                     msg += f""" om {vantijd}\n ⚡  € {prijs} \n"""

            if msg != "":
                return msg
            return False
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"

    def get_tomorrows_minus_price(self)->str:
        try:
            date = self.enddate
            data = self.get_prices(date=date, kind='e')
            msg = ""
            if data is not None:
                for d in data:
                    if d['price'] <= 0:
                        msg += f"""⚡ {d['fromtime']} -> € {d['price']:.2f}\n"""
            if msg != "":
                return f"Morgen {self.get_nice_day(date=date)} gaan we 0 en lager!\n{msg}"
            return False
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧 You found a error!"

    def get_todays_lowest_price(self, date:str = None)->str:
        try:
            data = self.get_lowest_price(date=date)
            msg = ""
            if data['elect'] is not None:
                msg += f"""Laagste prijzen ⚡ {self.get_nice_day(date=date)}\n"""
                for d in data['elect']:
                    msg += f"""{d['fromtime']} -> € {d['price']:.2f}\n"""

            if data['gas'] is not None:
                msg += f"""\nPrijzen voor 🔥 op {self.get_nice_day(date=date)}\n"""
                for d in data['gas']:
                    if d['fromtime'] == '06:00':
                        msg += f"""vanaf 6 uur -> € {d['price']:.2f}\n"""
                    elif d['fromtime'] == '05:00':
                        msg += f"""tot 6 uur -> € {d['price']:.2f}\n"""
            if msg == "":
                return "Sorry! Er is geen data beschikbaar!"

            return msg
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"

    def get_todays_highest_price(self, date:str = None)->str:
        try:
            data = self.get_highest_price(date=date)
            msg = ""
            if data['elect'] is not None:
                msg += f"""Hoogste prijzen ⚡ {self.get_nice_day(date=date)}\n"""
                for d in data['elect']:
                    msg += f"""{d['fromtime']} € {d['price']:.2f}\n"""

            if data['gas'] is not None:
                msg += f"""\nPrijzen voor 🔥 op {self.get_nice_day(date=date)}\n"""
                for d in data['gas']:
                    if d['fromtime'] == '06:00':
                        msg += f"""vanaf 6 uur -> € {d['price']:.2f}\n"""
                    elif d['fromtime'] == '05:00':
                        msg += f"""tot 6 uur -> € {d['price']:.2f}\n"""
            if msg == "":
                return "Sorry! Er is geen data beschikbaar!"

            return msg
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"

    def get_highest_price(self, date:str = None)->dict:
        try:
            if date is None:
                date = self.now.strftime("%Y-%m-%d")
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            gasdata = esql.get_high_prices(date=date, kind='g')
            electdata = esql.get_high_prices(date=date, kind='e')
            esql = None
            return {'gas': gasdata, 'elect': electdata}
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"

    def get_lowest_price(self, date:str = None)->dict:
        try:
            if date is None:
                date = self.now.strftime("%Y-%m-%d")

            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            gasdata = esql.get_low_prices(date=date, kind='g')
            electdata = esql.get_low_prices(date=date, kind='e')
            esql = None
            return {'gas': gasdata, 'elect': electdata}
        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧  Je hebt een foutje gevonden!"

    def get_cur_price(self, date:str = None, time:str = None)->str:
        try:
            if date is None:
                date = self.today

            if time is None:
                time = self.current_hour

            data = self.get_prices(date);
            gas = None
            elect = None

            for v in data:
                if v['kind'] == 'e' and v['fromtime'] == time:
                    elect = v
                if v['kind'] == 'g' and v['fromtime'] == time:
                    gas = v

            return f"""Huidige prijzen ({elect['fromtime']}-{self.next_hour}):
⚡ € {elect['price']:.2f}
🔥 € {gas['price']:.2f}"""

        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧 You found a error!"

    def get_nice_day(self, date:str = None)-> str:
        try:
            if date is None:
                date = self.today

            date = f"{date} 01:01:01"
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            day = dt.strftime("%d")
            weekday = self.weekdays[dt.weekday()]
            month_int = int(dt.strftime("%m"))
            month = self.months[month_int]

            return f"{weekday} {day} {month}"

        except Exception as e:
            log.error(e)
            return "Great Scott! 🚧 You found a error!"


    def get_todays_prices(self, date:str = None)->str:
        try:
            if date is None:
                date = self.tomorrow.strftime("%Y-%m-%d")
            esql = EnergiePrijzen_SQL(dbname=self.dbname )
            esql.connection()
            data = esql.get_prices(date=date)
            message = f"Prijzen van {self.get_nice_day(date=date)}\n"
            gas_voor = ""
            gas_na = ""
            for v in data:
                if v['kind'] == 'e':
                    # elect.append(v)
                    message += f"⚡ {v['fromtime']} -> € {v['price']:.2f}\n"
                if v['kind'] == 'g':
                    tijd = int(v['fromtime'][:-3])
                    if tijd <= 5:
                        gas_voor = f"🔥 tot 06:00 € {v['price']:.2f}\n"
                    else:
                        gas_na = f"🔥 na 06:00 € {v['price']:.2f}\n"

            message += "\n" + gas_voor + gas_na

            return message
        except Exception as e:
            log.error(e)
            return "Sorry, er ging iets fout! Probeer het later nog een keer."
        finally:
            esql.close()

    # Met name wanneer de prijs negatief gaat zou ik een melding willen

    # Wil je op dat moment een melding? Dus om 5 voor 12 als hij om 12 uur negatief wordt?
    # Theo van der Sluijs: Of een dag van te voren? Of....
    # Jan-Willem van der Wel: Beide

if __name__ == "__main__":
    EP = EnergiePrijzen(dbname="")
    EP.set_dates()
    EP.get_lowest_price()
    EP.get_cur_price()
