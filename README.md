#  Energie Prijzen Bot

Een Telegram bot die de dagelijkse actuele inkoop energie prijzen verwerkt en toont.

##  Omschrijving
Een Telegram bot die de dagelijkse actuele inkoop energie prijzen verwerkt en toont die gebruikt worden door Frank Energie, ANWB, EnergieZero, EasyEnergy, Tibber, Nieuwestroom, LeasePlan Energy, MijnDomein Energie.

Blijf up to date met de laagste stroom en gas tarieven.

Je hoeft zelf dit script niet te draaien als je nu al informatie wilt ontvangen. Open telegram en meld je aan bij de telegram [@EnergiePrijzen_bot](https://t.me/EnergiePrijzen_bot)

**Vergeet niet te doneren!**
[Doneer voor een kop koffie](https://donorbox.org/tvdsluijs-github)

##  Opstarten
Als je dit script wilt draaien kan dat direct via python
`src/python main.py`

of via de docker file
`docker build -t energie-prijzen-bot .`

ga daarna in de data folder staan en
`docker run -d energie-prijzen-bot -v $(pwd)/data:/src/data`



Vergeet niet dat je een Telegram bot moet aanmaken en daar de HTTP API Token moet kopiëren.

Een Telegram bot maak je via de @BotFather

De Token plaats je in `./config/config.conf` een voorbeeld van de config vind je in config.sample

###  Afhankelijkheden
- Python 3.8 (minimum)
- Telegram bot token
- Docker

#### Docker extra's

**Lijstje van al je docker containers**
`docker ps -a`

**Lijstje van alle container ids**
`docker ps -aq`

**Vind het pad naar de data**
`docker volume inspect <dockerid>`

**Data staat in**
/var/lib/docker/volumes/<dockerid>/_data

**Stop and verwijder container**
docker stop CONTAINER_ID
docker rm CONTATINER_ID

**Docker log files**
docker container logs CONTATINER_ID

###  Installeren

Voordat je main.py kan draaien moet je eerst een environment maken

`python -m venv .venv`

Daarna (als je env is opgestart) draai je pip install

`pip  install  --no-cache-dir  -r  /src/requirements.txt`

En daarna kan je het script draaien!

`python main.py`

Je kan natuurlijk de docker draaien
 `docker build -t energie-prijzen-bot .`

en daarna
`docker run -d energie-prijzen-bot`

Deze doet alles voor je automatisch.

##  Help

Heb je hulp nodig in de Bot?

`/help`

Heb je problemen bij dit script? Stuur dan een berichtje aan
info@itheo.tech

##  Auteurs

[Theo van der Sluijs](https://itheo.tech)

##  Versiegeschiedenis

*  0.1

*  Initial Release



##  MIT License

Copyright (c) 2022 Theo van der Sluijs

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



##  Dankbetuigingen

* [Github photo by Daniel Reche via Pexels](https://www.pexels.com/@daniel-reche-718241)

* [Python Telegram Bot]([https://python-telegram-bot.org](https://python-telegram-bot.org/))

* [dynamische-energieprijzen.nl](https://www.dynamische-energieprijzen.nl/actuele-energieprijzen/)

* [mdvmine](https://tweakers.net/gallery/78806/) heeft diverse verbeteringen en verbeteringen gestuurd.

