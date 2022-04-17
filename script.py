import requests as r
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


def getAFCUCars():
    afcu_url = 'https://repos.americafirst.com'

    page = r.get(afcu_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = []

    for element in soup.find_all('div', class_='card mb-3'):
        car_title = element.select(selector='.card-title')[0].text.strip()
        car_details = []
        for li in element.select('ul.text-secondary li'):
            car_details.append(li.text)

        car_bid = element.find(string=re.compile('Current High Bid'))
        if car_bid:
            car_bid_price = car_bid.parent.select('span')[0].text.strip()
        else:
            car_bid_price = ''

        car_bin = element.find(string=re.compile('Buy it Now'))
        if car_bin:
            car_bin_price = car_bin.parent.select('span')[0].text.strip()
        else:
            car_bin_price = ''

        car_bid_end_date = element.find(string=re.compile('Bidding Ends'))[14:]

        car_image_src = '{}{}'.format(afcu_url, element.select_one(selector='img').attrs['src'])

        car_details_url = '{}{}'.format(afcu_url, element.select_one(selector='.card-footer a.btn.btn-primary').attrs['href'])

        car_info = {
            'title': car_title,
            'details': ' '.join(car_details),
            'bid_price': car_bid_price,
            'bin_price': car_bin_price,
            'bid_end_date': car_bid_end_date,
            'image': car_image_src,
            'url': car_details_url,
            'source': "AFCU"
        }

        results.append(car_info)
    return results

def writeData(listOfCars):    
    #current_datetime = datetime.now(ZoneInfo("US/Mountain")).strftime("%Y-%m-%d %H:%M:%S %Z")
    with open('cars.json', 'w') as f:
        json.dump(listOfCars, f, indent=4)

def main():
    cars = []
    cars += getAFCUCars()
    writeData(cars)


if __name__ == '__main__':
    main()
