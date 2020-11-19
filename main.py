import csv
import uuid

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from tinydb import TinyDB, Query

app = Flask(__name__)
db = TinyDB('./db.json')


@app.route('/check_card')
def check_card():
    # nimmt die erste karte
    # holt sich min preis
    # erhöht min preis um X
    # checkt ob aktueller preis < min preis
    # wenn:
    # print()
    with open('cardlist.csv', 'rt') as inp:
        reader = csv.reader(inp)
        row = next(reader)
        row = next(reader)

        response = requests.get(get_filtered_card(row[0], 1, 2))
        html = BeautifulSoup(response.text, 'html.parser')
        lowest_price = html.find("dt", text=["From", "ab"]).findNext("dd").string
        lowest_price = convert_to_float(lowest_price)
        if lowest_price < 300:
            print("Neuer Tiefstpreis: " + str(lowest_price) + "€")

    return "nice"


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
        save_details()

    return render_template('index.html')


def save_details():
    locale = request.form.get("locale")
    foil = request.form.get("foil")
    mail = request.form.get("mail")
    notification_price = request.form.get("price")
    unique_id = str(uuid.uuid4())
    card_link = get_base_url(request.form.get("cardlink")) + '?language={}&isFoil={}'.format(locale, foil)

    # grab current price
    response = requests.get(card_link)
    html = BeautifulSoup(response.text, 'html.parser')
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
    app.run()
