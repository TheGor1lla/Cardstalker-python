import csv
import os
import uuid

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def card_stalker():
    if request.method == "POST":
        # TODO popup if successful
        save_details()

    return render_template('index.html')


def save_details():
    cardlink = request.form.get("cardlink")
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

        # grab current price (+ name?)
        csv_writer.writerow([cardlink, locale, foil, mail, '', price, unique_id])
    return cardlink + '?language={}&isFoil={}'.format(locale, foil)


if __name__ == '__main__':
    app.run()
