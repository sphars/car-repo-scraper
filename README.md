# Car Repo Scraper
A scraper to find and notify when new cars are posted on repossession websites, using GitHub Actions and [ntfy.sh](https://ntfy.sh). The script is ran once a day.

## Get Notified
If you want to get notified when a car is posted, you can download the [ntfy.sh mobile app](https://ntfy.sh/docs/subscribe/phone/) (Android only, iOS coming one day) or use the [web app](https://ntfy.sh/app) and subscribe to **utah-car-repos** as the topic.

When a notification comes in, it'll show the car, current price, details (if available) and an image (if available; may have to download it from the notification). Tapping on the notification will launch your browser to view the car's listing.

## Current Repo Sites
Currently targets only repossession websites in Utah.
 - [America First Credit Union](https://repos.americafirst.com)

## Acknowledgments
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for scraping library  
[ntfy.sh](https://ntfy.sh) for sending notifications  
