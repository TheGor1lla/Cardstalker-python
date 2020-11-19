import csv
import os
import uuid

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/check_card')
def check_card():
    # nimmt die erste karte
    #holt sich min preis
    #erhöht min preis um X
    #checkt ob aktueller preis < min preis
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
            print("Neuer Tiefstpreis: "+ str(lowest_price)+"€")


    return "nice"


@app.route('/delete/<card_id>')
def delete_card(card_id):
    with open('cardlist.csv', 'rt') as inp, open('first_edit.csv', 'wt', newline='') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            if row[6] != card_id:
                writer.writerow(row)
            else:
                cardname = row[0]
    os.remove('cardlist.csv')
    os.rename('first_edit.csv', 'cardlist.csv')
    return "{} deleted".format(cardname)


@app.route('/', methods=["GET", "POST"])
def card_stalker():
    if request.method == "POST":
        # TODO popup if successful
        save_details()

    return render_template('index.html')


def save_details():
    cardlink = get_base_url(request.form.get("cardlink"))
    locale = request.form.get("locale")
    foil = request.form.get("foil")
    mail = request.form.get("mail")
    price = request.form.get("price")
    unique_id = str(uuid.uuid4())

    with open('cardlist.csv', mode='a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        if os.stat("cardlist.csv").st_size == 0:
            fields = ['cardlink', 'locale', 'foil', 'mail', 'lowestRecordedPrice', 'maxReactionPrice', 'uuid']
            csv_writer.writerow(fields)

        #grab current price
        response = requests.get(get_filtered_card(cardlink, locale, foil))
        html = BeautifulSoup(response.text, 'html.parser')
        lowest_price = html.find("dt", text=["From", "ab"]).findNext("dd").string
        lowest_price = convert_to_float(lowest_price)

        csv_writer.writerow([cardlink, locale, foil, mail, lowest_price, price, unique_id])


def get_base_url(url):
    return url.split('?')[0]

def get_filtered_card(cardlink, locale, foil):
    return (cardlink + '?language={}&isFoil={}'.format(locale, foil))

def convert_to_float(string):
    string = string[:-2]
    price = float(string.replace(',', '.'))
    return price

if __name__ == '__main__':
    app.run()
