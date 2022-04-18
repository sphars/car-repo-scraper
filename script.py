import requests as r
import json, re
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

def getAFCUCars():
    afcu_url = 'https://repos.americafirst.com'

    page = r.get(afcu_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = []

    for element in soup.find_all('div', class_='card mb-3'):
        car_title = element.select_one(selector='.card-title').text.strip()
        car_details = []
        for li in element.select('ul.text-secondary li'):
            car_details.append(li.text)

        car_bid = element.find(string=re.compile('Current High Bid'))
        if car_bid:
            car_bid_price = car_bid.parent.select_one('span').text.strip()
        else:
            car_bid_price = ''

        car_bin = element.find(string=re.compile('Buy it Now'))
        if car_bin:
            car_bin_price = car_bin.parent.select_one('span').text.strip()
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

def getNewCars(current_cars):
    previous_cars = []
    with open('cars.json', 'r') as f:
        previous_cars = json.load(f)

    # get the set of unique urls in list of previous cars
    previous_cars_bucket = set(car["url"] for car in previous_cars['cars'])
    
    # get the list of cars from current cars by set of urls
    new_cars = []
    new_cars.extend(car for car in current_cars if car['url'] not in previous_cars_bucket)

    return new_cars

def sendNotifications(new_cars):
    for car in new_cars:
        data = "{0} | {1}\n{2}".format(car['title'], car['bin_price'] or car['bid_price'], car['details'])
        r.post("https://ntfy.sh/utah-car-repos",
            data=data,
            headers={
                "Title": "New Car Posted",
                "Tags": "car",
                "Click": car['url'],
                "Attach": car['image']
            })


def writeData(list_of_cars):    
    current_datetime = datetime.now(ZoneInfo("US/Mountain")).strftime("%Y-%m-%d %H:%M:%S %Z")
    final_data = {
        "last_updated": current_datetime,
        "cars": list_of_cars
    }
    with open('cars.json', 'w') as f:
        json.dump(final_data, f, indent=4)

def main():
    current_cars = []
    current_cars += getAFCUCars()

    new_cars = getNewCars(current_cars)
    if(new_cars):
        sendNotifications(new_cars)
        writeData(current_cars)


if __name__ == '__main__':
    main()
