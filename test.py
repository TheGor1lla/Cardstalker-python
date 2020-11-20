import cProfile
import time

import requests
from bs4 import BeautifulSoup

def convert_to_float(string):
    string = string[:-2]
    price = float(string.replace(',', '.'))
    return price


def easy():
    print("start easy: ")
    print(time.perf_counter())
    url = "https://www.cardmarket.com/en/Magic/Products/Singles/Commander-Collection-Green/Worldly-Tutor?language=1&isFoil=Y"
    response = requests.get(url)
    price_item = BeautifulSoup(response.text, 'lxml').find("dt", text=["From", "ab"]).findNext("dd").string
    price = convert_to_float(price_item)
    print("end easy: ")
    print(time.perf_counter())

def easy_bew():
    print("start easy_bew: ")
    print(time.perf_counter())
    url = "https://www.cardmarket.com/en/Magic/Products/Singles/Commander-Collection-Green/Worldly-Tutor?language=1&isFoil=Y"
    response = requests.get(url)
    price_item = convert_to_float(
        BeautifulSoup(response.text, 'html.parser').find("dt", text=["From", "ab"]).findNext("dd").string)
    print("end easy_bew: ")
    print(time.perf_counter())

easy()
