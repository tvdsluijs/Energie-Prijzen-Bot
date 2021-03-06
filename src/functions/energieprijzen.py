from ast import Constant
import os, sys
import json
import requests
import logging

from datetime import datetime, timedelta
from dateutil import parser, tz

from time import sleep

from telegram import PassportElementError
from functions.energieprijzen_sql import EnergiePrijzen_SQL

from entsoe import EntsoePandasClient
import pandas as pd

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
        self.current_hour = None
        self.current_date_time = None
        self.next_hour = None
        self.current_hour_short = None
        self.lowest_electricity = None
        self.highest_electricity = None

        self.prices = {}
        self.foutmelding = "🚧 Great Scott 🚧 \n Je bent tegen een fout aangelopen"

        self.morgen = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00']
        self.middag = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']

        self.weekdays = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
        self.months = ['', 'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']
        self.nice_day = None #net uitgeschreven dag donderdag 22 april

    @staticmethod
    def get_timestamp(time_stamp:str = "", UTC:bool = True)->dict:
        try:
            if UTC:
                from_zone = tz.gettz('UTC')
                to_zone = tz.gettz('CET')

                d = parser.parse(time_stamp)

                utc = d.replace(tzinfo=from_zone)
                cet = utc.astimezone(to_zone)

                datum = cet.strftime('%Y-%m-%d')  #==> '1975-05-14'
                tijd = cet.strftime('%H:00')  #==> '18:00'
            else:
                datum = time_stamp.strftime('%Y-%m-%d')  #==> '1975-05-14'
                tijd = time_stamp.strftime('%H:00')  #==> '18:00'

            return {'datum': datum, 'tijd': tijd}
        except Exception as e:
           log.error(e)

    def set_dates(self)->None:
        try:
            self.now = datetime.now()

            yesterday_ts = self.now + timedelta(days=-1)
            tomorrow_ts = self.now + timedelta(days=+1)
            next_hour_ts = self.now + timedelta(hours=+1)

            self.today = self.now.strftime("%Y-%m-%d")
            self.yesterday = yesterday_ts.strftime("%Y-%m-%d")
            self.tomorrow = tomorrow_ts.strftime("%Y-%m-%d")

            self.current_hour = self.now.strftime("%H:00")
            self.current_hour_short = int(self.now.strftime("%H"))

            self.next_hour = next_hour_ts.strftime("%H:00")
            self.current_date_time = self.now.strftime("%Y-%m-%d %H:%M")

        except Exception as e:
            log.error(e)

    @staticmethod
    def get_next_hour(hours:int = 1):
        next_hour = datetime.now() + timedelta(hours=+hours)
        return next_hour.strftime("%H:00")

    def get_entsoe_data(self, startdate:str = "", enddate:str = "", entsoe_key:str=None)->json:
        try:
            if entsoe_key is None or entsoe_key == "":
                raise Exception("We don't have a entsoe key")
            if startdate == "":
                yesterday = datetime.now() + timedelta(days=-1)
                periodStart = yesterday.strftime("%Y%m%d0001") #yyyyMMddHHmm
            if enddate == "":
                tomorrow = datetime.now() + timedelta(days=+1)
                periodEnd = tomorrow.strftime("%Y%m%d2359") #yyyyMMddHHmm

            startdate = pd.Timestamp(periodStart, tz='Europe/Brussels')
            enddate = pd.Timestamp(periodEnd, tz='Europe/Brussels')
            data = {}
            client = EntsoePandasClient(api_key=entsoe_key)

            country_code = 'NL'
            ts = client.query_day_ahead_prices(country_code,start=startdate,end=enddate)
            lines = []
            table = ts.to_dict()

            for k,v in table.items():
                dt = pd.to_datetime(k)

                # datum_tijd = dt.strftime("%Y-%m-%dT%H:%M:00+0200")
                kwh_p = float(v/1000)
                lines.append({'price': kwh_p, 'readingDate': dt, 'UTC': False})
            if lines is None:
                return False

            data['Prices'] = lines
            return data
        except Exception as e:
            log.error(e)
            return False

    def get_energyzero_data(self, startdate:str = "", enddate:str = "",kind:str = ENERGIE.value)->json:
        try:
            if startdate == "":
                startdate = self.yesterday
            if enddate == "":
                enddate = self.tomorrow
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
            return False
        except Exception as e:
            log.error(e)
            return False

    def get_history(self, startdate:str = "2017-01-01", enddate:str = "2017-01-02", kind:int = 1)->None:
        try:
            start = datetime.strptime(startdate, "%Y-%m-%d")

            while start <= self.now:
                # Get datax
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
                raise Exception('No data to save')
            if kind is None:
                raise Exception('No power kind')

            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            esql.connection()

            str_kind = ""
            match kind:
                case self.GAS.value:
                    str_kind = 'g'
                case self.ENERGIE.value:
                    str_kind = 'e'
                case _:
                    raise Exception('No correct power kind')


            for row in data['Prices']:
                prices = {}
                #the entsoe price-timestamps as Europe/Amsterdam
                try:
                    UTC = row['UTC']
                except KeyError:
                    # the enerzyzero json does not have a UTC key so we set it on true
                    UTC = True

                efrom = self.get_timestamp(time_stamp=row['readingDate'],UTC=UTC)
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
                        msg = f"""
Om {d['fromtime']} gaat de ⚡ prijs naar\n"""
                        price = self.dutch_floats(price=d['price'])
                        msg += f"""{price}\n"""
            if msg != "":
                return msg
            return False
        except KeyError as e:
            log.error(e)
            return self.foutmelding
        except Exception as e:
            log.error(e)
            return self.foutmelding

    def get_ochtend_users(self, hour:int = None)->list:
        try:
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            users = esql.get_ochtend_users(hour=hour)
            users.append(0)
            return users
        except Exception as e:
            log.error(e)
        finally:
            esql.close()

    def ochtend_message(self, )->str:
        try:
            data = self.get_low_high()
            fromtime_low = data['elect_low'][0]['fromtime']
            low_price = data['elect_low'][0]['price']
            fromtime_high = data['elect_high'][0]['fromtime']
            high_price = data['elect_high'][0]['price']
            int_hour_low = int(fromtime_low[:2]) + 1
            int_hour_high = int(fromtime_high[:2]) + 1
            totime_low = f"{int_hour_low:02d}:00"
            totime_hight = f"{int_hour_high:02d}:00"
            return f"Vandaag is de inkoopprijs van stroom per kWh het laagst tussen {fromtime_low} en {totime_low} (€ {low_price}) en het hoogst tussen {totime_hight} en {fromtime_high} (€ {high_price})."
        except Exception as e:
            log.error(e)
            return False

    def get_low_high(self, date:str = None)->dict:
        try:
            if date is None:
                date = self.today
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            elect_low = esql.get_low_prices(date=date, kind='e')
            elect_high = esql.get_high_prices(date=date, kind='e')
            return {'elect_low': elect_low, 'elect_high': elect_high}
        except Exception as e:
            log.error(e)
            return self.foutmelding

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
                msg = f"""
Laagste prijs van {self.get_nice_day(date=date)}"""
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
                return f"""```{msg}```"""
            return False
        except Exception as e:
            log.error(e)
            return self.foutmelding

    def get_tomorrows_minus_price(self)->str:
        try:
            date = self.tomorrow
            data = self.get_prices(date=date, kind='e')
            msg_elec = ""
            if data is not None:
                for d in data:
                    if d['price'] <= 0:
                        price = self.dutch_floats(price=d['price'])
                        msg_elec += f"""{d['fromtime']} {price}\n"""
            if msg_elec != "":
                # {self.get_nice_day(date=date)}
                msg = f"""
Morgen gaat ⚡ onder 0
```
{msg_elec}```"""
                return msg
            return False
        except Exception as e:
            log.error(e)
            return self.foutmelding

    def get_todays_lowest_price(self, date:str = None)->str:
        try:
            data = self.get_lowest_price(date=date)
            msg = ""
            elect = ""
            gas = ""
            if data['elect'] is not None:
                msg_elec = f"\n{self.get_nice_day(date=date)}\nLaagste prijzen ⚡\n"
                for d in data['elect']:
                    price = self.dutch_floats(price=d['price'])
                    elect += f"{d['fromtime']} {price}\n"

                msg = f"""{msg_elec}```
{elect}```"""

            if data['gas'] is not None:
                msg_gas = f"\nPrijzen 🔥\n"
                for d in data['gas']:
                    price = self.dutch_floats(price=d['price'])
                    if d['fromtime'] == '06:00':
                        gas += f"vanaf 6 uur {price}\n"
                    elif d['fromtime'] == '05:00':
                        gas += f"tot 6 uur {price}\n"

                msg +=  f"""{msg_gas}```
{gas}```"""
            if msg == "":
                return "Sorry, er is geen data beschikbaar"
            return msg

        except Exception as e:
            log.error(e)
            return self.foutmelding

    def get_todays_highest_price(self, date:str = None)->str:
        try:
            data = self.get_highest_price(date=date)
            msg = ""
            elect = ""
            gas = ""
            if data['elect'] is not None:
                msg_elec = f"{self.get_nice_day(date=date)}\nHoogste prijzen ⚡\n"
                for d in data['elect']:
                    price = self.dutch_floats(price=d['price'])
                    elect += f"""{d['fromtime']} {price}\n"""

                msg = f"""{msg_elec}```
{elect}```"""

            if data['gas'] is not None:
                msg_gas = f"\nPrijzen 🔥\n"
                for d in data['gas']:
                    price = self.dutch_floats(price=d['price'])
                    if d['fromtime'] == '06:00':
                        gas += f"""vanaf 6 uur {price}\n"""
                    elif d['fromtime'] == '05:00':
                        gas += f"""tot 6 uur {price}\n"""
                msg +=  f"""{msg_gas}```
{gas}```"""
            if msg == "":
                return "Sorry, er is geen data beschikbaar"

            return msg
        except Exception as e:
            log.error(e)
            return self.foutmelding

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
            return self.foutmelding

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
            return self.foutmelding

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

            elect_price = self.dutch_floats(price=elect['price'])
            gas_price= self.dutch_floats(price=gas['price'])

            return f"""
Prijzen {elect['fromtime']}\-{self.next_hour}
⚡ {elect_price}
🔥 {gas_price}"""

        except Exception as e:
            log.error(e)
            return self.foutmelding

    def get_nice_day(self, date:str = None) -> str:
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
            return self.foutmelding

    def get_todays_prices(self, date:str = None)->str:
        try:
            if date is None:
                date = self.morgen
            esql = EnergiePrijzen_SQL(dbname=self.dbname)
            esql.connection()
            data = esql.get_prices(date=date)
            msg_elect = f"""{self.get_nice_day(date=date)}
Prijzen ⚡"""
            msg_gas =  f"Prijzen 🔥"
            gas_voor = ""
            gas_na = ""
            elec = ""
            msg = ""
            electra = {}

            for v in data:
                if v['kind'] == 'e':
                    price = self.dutch_floats(price=v['price'])
                    electra[v['fromtime']] = price
                if v['kind'] == 'g':
                    tijd = int(v['fromtime'][:-3])
                    if tijd <= 5:
                        price = self.dutch_floats(price=v['price'])
                        gas_voor = f"tot 06:00 {price}"
                    else:
                        price = self.dutch_floats(price=v['price'])
                        gas_na = f"na 06:00 {price}"

            for index,item in enumerate(self.morgen):
                elec += f"{self.morgen[index]} {electra[self.morgen[index]]}  {self.middag[index]} {electra[self.middag[index]]}\n"

            msg = f"""{msg_elect}```

{elec}```
{msg_gas}
```
{gas_voor}
{gas_na}```"""
            return msg
        except KeyError as e:
            log.error(f"Key niet gevonden in electra {e}")
        except Exception as e:
            log.error(e)
            return self.foutmelding
        finally:
            esql.close()

    @staticmethod
    def dutch_floats(price:float = None,f:str=':.3f')->str:
        return ('€ {'+f+'}').format(price).replace('.',',')

    # Met name wanneer de prijs negatief gaat zou ik een melding willen

    # Wil je op dat moment een melding? Dus om 5 voor 12 als hij om 12 uur negatief wordt?
    # Theo van der Sluijs: Of een dag van te voren? Of....
    # Jan-Willem van der Wel: Beide

if __name__ == "__main__":
    EP = EnergiePrijzen(dbname="")
    EP.set_dates()
    EP.get_lowest_price()
    EP.get_cur_price()
