import requests as r
import json, os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from datetime import datetime
from zoneinfo import ZoneInfo

# setup chrome
chrome_version = os.getenv("CHROME_VERSION", "119.0.6045.123")
print(f"Using Chrome {chrome_version}")
chrome_options = Options()
user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-extensions",
    "--no-sandbox",
    f"--user-agent={user_agent}"
]
for option in options:
    chrome_options.add_argument(option)

service = Service(log_output=1)
driver = webdriver.Chrome(options=chrome_options, service=service)

def get_afcu_cars():
    afcu_url = 'https://repos.americafirst.com'

    # load the webpage
    driver.get(afcu_url)
    driver.implicitly_wait(1)

    # get the cards
    cards = driver.find_elements(By.CSS_SELECTOR, "div[class = 'card mb-3']")
    print(f"Found {len(cards)} vehicles from AFCU")

    results = []
    if len(cards) > 0:
            
        for card in cards:
            # get car title
            car_title = card.find_element(By.CLASS_NAME, "card-title").text
            print(f"  {car_title}")

            # get car details
            details_elements = card.find_elements(By.CLASS_NAME, "list-inline-item")
            car_details = []
            for item in details_elements:
                car_details.append(item.text)

            # get current bid and buy now prices
            car_prices = card.find_elements(By.CSS_SELECTOR, ".h4.text-primary strong")
            car_bid_price = ""
            car_buy_now = ""
            if car_prices:
                car_bid_price = car_prices[0].text.strip()
                if len(car_prices) > 1:
                    car_buy_now = car_prices[1].text.strip()


            # get car bid end date
            car_bid_end_date = card.find_element(By.CSS_SELECTOR, ".card-text.small.mt-3").text[14:]

            # get the link to the image
            car_image_src = card.find_element(By.TAG_NAME, "img").get_attribute("src")
            car_image_url = f"{car_image_src}"

            # get the link to the details page
            car_details_url_value = card.find_element(By.CSS_SELECTOR, ".card-footer a.btn.btn-primary").get_attribute("href")
            car_details_url = f"{car_details_url_value}"

            # assemble data
            car_info = {
                'title': car_title,
                'details': ' '.join(car_details),
                'bid_price': car_bid_price,
                'bin_price': car_buy_now,
                'bid_end_date': car_bid_end_date,
                'image': car_image_url,
                'url': car_details_url,
                'source': "AFCU"
            }

            results.append(car_info)
            
    return results

def get_new_cars(current_cars):
    previous_cars = []
    with open('cars.json', 'r') as f:
        previous_cars = json.load(f)

    # get the set of unique urls in list of previous cars
    previous_cars_bucket = set(car["url"] for car in previous_cars['cars'])
    
    # get the list of cars from current cars by set of urls
    new_cars = []
    new_cars.extend(car for car in current_cars if car['url'] not in previous_cars_bucket)

    return new_cars

def send_notifications(new_cars):
    for car in new_cars:
        data = f"{car['title']} | {car['bid_price'] or car['bin_price']}\n{car['details']}"
        r.post("https://ntfy.sh/utah-car-repos",
            data=data,
            headers={
                "Title": "New Car Posted",
                "Tags": "car",
                "Click": car['url'],
                "Attach": car['image']
            })


def write_data(list_of_cars):    
    current_datetime = datetime.now(ZoneInfo("US/Mountain")).strftime("%Y-%m-%d %H:%M:%S %Z")
    final_data = {
        "last_updated": current_datetime,
        "cars": list_of_cars
    }
    with open('cars.json', 'w') as f:
        json.dump(final_data, f, indent=2)

def main():
    list_of_cars = []
    list_of_cars += get_afcu_cars()

    new_cars = get_new_cars(list_of_cars)
    if(new_cars):
        print(f"Found {len(new_cars)} new car{'s' if len(new_cars) != 1 else ''}")
        send_notifications(new_cars)
    else:
        print("No new cars found since last run")
    
    # write the updated data always due to new bids
    write_data(list_of_cars)


if __name__ == '__main__':
    main()
