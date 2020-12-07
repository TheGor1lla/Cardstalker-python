import logging
import uuid
from logging.handlers import SMTPHandler

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from flask_mail import Mail, Message
from tinydb import TinyDB, Query

app = Flask(__name__)
db = TinyDB('./db.json')
scheduler = BackgroundScheduler(daemon=True)
app.config.from_object('config.DevConfig')
# app.config.from_object('config.ProdConfig')
mail = Mail(app)


mail_handler = SMTPHandler(
    mailhost=app.config['MAIL_ERROR_HOST'],
    fromaddr=app.config['MAIL_ERROR_SENDER_ADDR'],
    toaddrs=app.config['MAIL_ERROR_TO_ADDR'],
    subject=app.config['MAIL_ERROR_SUBJECT']
)

mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(levelname)s] in %(module)s: %(message)s'
))

if not app.debug:
    app.logger.addHandler(mail_handler)


def check_card():
    for item in db:
        url = item.get('cardLink')
        lowest_price = item.get('lowestPrice')
        notification_price = item.get('notificationPrice')
        card_uuid = item.get('uuid')
        mail_addr = item.get('mail')

        response = requests.get(url)
        price_item = BeautifulSoup(response.text, 'lxml').find("dt", text=["From", "ab", "Available from"]).findNext("dd").string
        # ToDo if not N/A
        price = convert_price_to_float(price_item)

        if price != float(lowest_price):
            db.update({'lowestPrice': price}, Query().cardLink == url)

            if notification_price and price > float(notification_price):
                app.logger.info("Nothing new for " + url)
            else:
                with app.app_context():
                    card_info = {'url': url, 'lowest_price': lowest_price, 'price': price, 'card_uuid': card_uuid}
                    msg = Message("Cardnotifier here", recipients=[mail_addr])
                    msg.html = render_template('mail.html', data=card_info)
                    mail.send(msg)
                    app.logger.info("Sent mail for " + url + " to " + mail_addr
                                    + ", price changed from " + str(lowest_price) + " to " + str(price))
        app.logger.info("Nothing new for " + url)


@app.route('/delete/<card_id>')
def delete_card(card_id):
    query = Query()

    card_to_delete = db.get(query.uuid == card_id)
    db.remove(query.uuid == card_id)
    app.logger.info("Deleted " + card_to_delete.get('cardLink'))
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
    mail_form = request.form.get("mail")
    notification_price = request.form.get("price")
    unique_id = str(uuid.uuid4())
    card_link = get_base_url(request.form.get("cardLink")) + '?language={}&isFoil={}'.format(locale, foil)

    # grab current price
    response = requests.get(card_link)
    html = BeautifulSoup(response.text, 'lxml')
    lowest_price = html.find("dt", text=["From", "ab"]).findNext("dd").string
    # ToDo if not N/A
    lowest_price = convert_price_to_float(lowest_price)

    if notification_price:
        notification_price = float(notification_price)

    db.insert({'cardLink': card_link,
               'locale': locale,
               'foil': foil,
               'mail': mail_form,
               'notificationPrice': notification_price,
               'uuid': unique_id,
               'lowestPrice': lowest_price})

    app.logger.info("Added " + card_link + " for " + mail_form)


def get_base_url(url):
    return url.split('?')[0]


def convert_price_to_float(string):
    string = string[:-2]
    price = float(string.replace(',', '.'))
    return price


if __name__ == '__main__':
    scheduler.add_job(check_card, 'interval', hours=1)
    scheduler.start()
    app.run()
    # app.run(host='0.0.0.0', port=5000)
