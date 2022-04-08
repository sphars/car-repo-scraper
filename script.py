import requests as r
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

page = r.get('https://repos.americafirst.com')
soup = BeautifulSoup(page.content, 'html.parser')

car_cards = []
for element in soup.select('.card-body'):
    car_title = element.select('.card-title')[0].text
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

    car_info = {
        "title": car_title.strip(),
        "details": ' '.join(car_details),
        "bid_price": car_bid_price.strip(),
        "bin_price": car_bin_price.strip(),
        "bid_end_date": car_bid_end_date[14:]
    }

    car_cards.append(car_info)

repo_sources = []
repo_sources.append({"credit_union": "America First Credit Union", "cars": car_cards})

current_datetime = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
final_json = {
    "last_updated": current_datetime,
    "repo_sources":repo_sources
}
with open('cars.json', 'w') as f:
    json.dump(final_json, f)
