# live
# https://transparency.entsoe.eu/api?

# test
# https://iop-transparency.entsoe.eu/api?

from datetime import datetime, timedelta
import configparser
from dateutil import parser
import os, sys

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

# from entsoe import EntsoeRawClient
from entsoe import EntsoePandasClient
import pandas as pd

os.environ['TZ'] = 'Europe/Amsterdam'

dir_path = os.path.dirname(os.path.realpath(__file__))
config_folder = os.path.join(dir_path, 'src','config')

config_file = os.path.join(config_folder, 'config.conf')
config = configparser.ConfigParser()
config.read(config_file)
securityToken = config['entsoe']['key']

now = datetime.now()
yesterday = datetime.now() + timedelta(days=-1)
tomorrow = datetime.now() + timedelta(days=+1)

today = now.strftime("%Y%m%d%H00") #yyyyMMddHHmm

periodStart = yesterday.strftime("%Y%m%d%H00") #yyyyMMddHHmm
periodEnd = tomorrow.strftime("%Y%m%d%H00") #yyyyMMddHHmm

entsoe_start = pd.Timestamp(periodStart, tz='Europe/Brussels')
entsoe_end = pd.Timestamp(periodEnd, tz='Europe/Brussels')

# client = EntsoeRawClient(api_key=securityToken)
client = EntsoePandasClient(api_key=securityToken)

country_code = 'NL'
ts = client.query_day_ahead_prices(country_code,start=entsoe_start,end=entsoe_end)

table = ts.to_dict()
for k,v in table.items():
    dt = pd.to_datetime(k)

    datum = dt.strftime("%Y-%m-%d")
    tijd = dt.strftime("%H:00")

    kwh_p = round(v/1000,3)
    print(k, datum, tijd, v, kwh_p)


# BZN|NL
# https://transparency.entsoe.eu/api?securityToken=MYTOKEN&documentType=A65&processType=A16&outBiddingZone_Domain=10YCZ-CEPS-----N&periodStart=201512312300&periodEnd=201612312300

# https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show?name=&defaultValue=false&viewType=TABLE&areaType=BZN&atch=false&dateTime.dateTime=26.04.2022+00:00|CET|DAY&biddingZone.values=CTY|10YNL----------L!BZN|10YNL----------L&resolution.values=PT60M&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)

# url = f"https://iop-transparency.entsoe.eu/api?securityToken={securityToken}&documentType={DocumentType}&processType={ProcessType}&outBiddingZone_Domain={outbiddingzonedomain}&periodStart={periodStart}&periodEnd={periodEnd}"