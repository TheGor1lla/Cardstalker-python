import os
import uuid
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from tinydb import TinyDB, Query
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from logging.handlers import SMTPHandler

app = Flask(__name__)
db = TinyDB('./db.json')
scheduler = BackgroundScheduler(daemon=True)

mail_handler = SMTPHandler(
    mailhost='127.0.0.1',
    fromaddr='cardstalker@gor1lla.de',
    toaddrs=['admin@gor1lla.de'],
    subject='Application Error'
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

if not app.debug:
    app.logger.addHandler(mail_handler)


def check_card():
    for item in db:
        url = item.get('cardLink')
        lowest_price = item.get('lowestPrice')
        notification_price = item.get('notificationPrice')
        card_uuid = item.get('uuid')

        response = requests.get(url)
        price_item = BeautifulSoup(response.text, 'lxml').find("dt", text=["From", "ab"]).findNext("dd").string
        price = convert_to_float(price_item)

        if price != float(lowest_price):
            db.update({'lowestPrice': price}, Query().cardLink == url)

            if notification_price and price >= float(notification_price):
                app.logger.info("Nothing new for "+url)
            else:
                card_info = {'url': url, 'lowest_price': lowest_price, 'price': price, 'card_uuid': card_uuid}
            return render_template('mail2.html', data=card_info)
        app.logger.info("Nothing new for "+url)


@app.route('/delete/<card_id>')
def delete_card(card_id):
    query = Query()

    card_to_delete = db.get(query.uuid == card_id)
    db.remove(query.uuid == card_id)
    return "{} deleted".format(card_to_delete.get('cardLink'))


@app.route('/', methods=["GET", "POST"])
def card_stalker():
    if request.method == "POST":
        # TODO popup if successful
        # TODO run in background
        save_details()

    return render_template('index.html')


def save_details():
    locale = request.form.get("locale")
    foil = request.form.get("foil")
    mail = request.form.get("mail")
    notification_price = request.form.get("price")
    unique_id = str(uuid.uuid4())
    card_link = get_base_url(request.form.get("cardLink")) + '?language={}&isFoil={}'.format(locale, foil)

    # grab current price
    response = requests.get(card_link)
    html = BeautifulSoup(response.text, 'lxml')
    lowest_price = html.find("dt", text=["From", "ab"]).findNext("dd").string
    lowest_price = convert_to_float(lowest_price)

    db.insert({'cardLink': card_link,
               'locale': locale,
               'foil': foil,
               'mail': mail,
               'notificationPrice': notification_price,
               'uuid': unique_id,
               'lowestPrice': lowest_price})


def get_base_url(url):
    return url.split('?')[0]


def convert_to_float(string):
    string = string[:-2]
    price = float(string.replace(',', '.'))
    return price

if __name__ == '__main__':
    scheduler.add_job(check_card(), 'interval', seconds=1)
    # scheduler.start()
    app.run()
