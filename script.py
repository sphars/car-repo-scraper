import requests as r
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

afcu_url = 'https://repos.americafirst.com'

page = r.get(afcu_url)
soup = BeautifulSoup(page.content, 'html.parser')

car_cards = []
for element in soup.find_all('div', class_='card mb-3'):
    car_title = element.select(selector='.card-title')[0].text
    car_details = []
    for li in element.select('ul.text-secondary li'):
        car_details.append(li.text)
    
    car_bid = element.find(string=re.compile('Current High Bid'))
    if car_bid:
        car_bid_price = car_bid.parent.select('span')[0].text
    else:
        car_bid_price = ''
    
    car_bin = element.find(string=re.compile('Buy it Now'))
    if car_bin:
        car_bin_price = car_bin.parent.select('span')[0].text
    else:
        car_bin_price = ''
    
    car_bid_end_date = element.find(string=re.compile('Bidding Ends'))

    car_image_src = "{}{}".format(afcu_url, element.select_one(selector='img').attrs['src'])

    car_info = {
        "title": car_title.strip(),
        "details": ' '.join(car_details),
        "bid_price": car_bid_price.strip(),
        "bin_price": car_bin_price.strip(),
        "bid_end_date": car_bid_end_date[14:],
        "image": car_image_src
    }

    car_cards.append(car_info)

repo_sources = []
repo_sources.append({"credit_union": "America First Credit Union", "cars": car_cards})

current_datetime = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
results = {
    "last_updated": current_datetime,
    "repo_sources":repo_sources
}
with open('cars.json', 'w') as f:
    json.dump(results, f, indent=4)
