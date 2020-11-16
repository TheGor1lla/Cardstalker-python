import requests
from bs4 import BeautifulSoup


def check_cards():
    url = "https://www.cardmarket.com/en/Magic/Products/Singles/Commander-Collection-Green/Worldly-Tutor?isFoil=Y"

    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')
    # print(BeautifulSoup.prettify(html))

    lowest_price = html.find("dt", text=["From", "ab"]).findNext("dd").string
    print("Scrapped price " + lowest_price)
    if convert_to_float(lowest_price) < 50:
        print("I'll do something")


def convert_to_float(string):
    string = string[:-2]
    price = float(string.replace(',', '.'))
    return price


'''
TODO:                           
* Run every hour       
* Iterate over csv, for every entry:
** check if lowest Price changed
if Y: send mail with new price
 update lowest price in csv
 send mail with information                                                             
                                                                                                                                                                                                                                                                        
On submit:                                                                                                              
 * Grab lowest price, save in csv                                                                                                                                                                                                                
'''

if __name__ == '__main__':
    check_cards()
