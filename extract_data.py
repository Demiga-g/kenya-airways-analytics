import argparse
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser()

parser.add_argument('--input_airline', required=True,
                    help='name of airline to scrape')
parser.add_argument('--output_data', required=True,
                    help='how to name the scrapped csv file')
parser.add_argument('--input_page_size', required=False,
                    help='the size of reviews to extract from a single page')
parser.add_argument('--input_sleep_time', required=True,
                    help='time (seconds) taken before scrapping the next page')

args = parser.parse_args()
input_airline = args.input_airline
output_data = args.output_data
input_page_size = args.input_page_size
input_sleep_time = args.input_sleep_time


data_list = []
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
base_url ="https://www.airlinequality.com/airline-reviews"


def get_soup(page_count, page_size=20):
    headers = {
        "User-Agent": user_agent}
    url = f"{base_url}/{input_airline}/page/{page_count}/?sortby=post_date%3ADesc&pagesize={page_size}"
    response = requests.get(url, headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        cleaned_soup = soup.find_all("article", itemprop="review")
        return cleaned_soup
    else:
        print("Error in getting soup")


def extract_raw_data(cleaned_soup):
    # extract the data from the soup
    # articles = soup.find_all("article", itemprop="review")

    for article in cleaned_soup:

        ######## DATA OUTSIDE TABLE ########

        # review publication date
        try:
            date_published = article.find("time", itemprop="datePublished").get('datetime')
        except AttributeError:
            date_published = 'NA'

        # review title
        try:
            title = article.find("h2", class_="text_header").text
            title = re.sub(r'[“”"]', '', title)
        except AttributeError:
            title = 'NA'

        # is trip verified or not?
        try:
            trip_verification = article.find("div", class_="text_content", itemprop="reviewBody")
            string_pattern = r'(Trip Verified|Not Verified|Verified Review)'
            trip_verification = re.search(string_pattern, trip_verification.text).group(1)
        except AttributeError:
            trip_verification = 'NA'

        # passenger's country
        try:
            country = article.find("h3", class_="text_sub_header userStatusWrapper")
            country = re.search(r'\((.*?)\)', country.text).group(1)
        except AttributeError:
            country = 'NA'

        # passenger's trip review
        try:
            review = article.find("div", class_="text_content", itemprop="reviewBody").text
            if review != 'NA':
                review_parts = review.split('|', 1)
                review = review_parts[1].strip() if len(review_parts) > 1 else review_parts
        except AttributeError:
            review = 'NA'

        # passenger's other reviews
        try:
            other_reviews = article.find("span", class_="userStatusReviewCount").text
            other_reviews = int(re.search(r'\d+', other_reviews).group(0))
        except AttributeError:
            other_reviews = 'NA'

        # passenger's rating out of 10
        try:
            rating_10 = article.find("span", itemprop="ratingValue").get_text(strip=True)
        except AttributeError:
            rating_10 = 'NA'

        general_dict = {
            'date_published': date_published,
            'summary_title': title,
            'country': country,
            'trip_verified': trip_verification,
            'review': review,
            'other_reviews': other_reviews,
            'ratings_10': rating_10,
        }

        ######## DATA INSIDE TABLE ########

        # other passenger details provided in table
        passenger_details = ["aircraft", "type_of_traveller", "cabin_flown", "route", "recommended"]
        passenger_details_dict = {}

        for detail in passenger_details:
            passenger_detail = article.find("td", class_="review-rating-header " + detail)
            try:
                passenger_detail = passenger_detail \
                    .find_next('td', class_="review-value") if passenger_detail else 'NA'
                passenger_details_dict[detail] = passenger_detail.get_text(strip=True) \
                    if passenger_details else 'NA'
            except AttributeError:
                pass

        # passenger ratings about other issues
        ratings_dict = {}

        services_ratings = ['seat_comfort', 'cabin_staff_service',
                            'food_and_beverages', 'inflight_entertainment',
                            'ground_service', 'wifi_and_connectivity', 'value_for_money']

        for rating in services_ratings:
            target_stars = article.find('td', class_="review-rating-header " + rating)
            try:
                rating_td = target_stars.find_next('td', class_='review-rating-stars') if target_stars else 'NA'
                ratings_dict[rating] = len(rating_td.find_all('span', class_='star fill')) if rating_td else 'NA'
            except AttributeError:
                pass

        data = general_dict | passenger_details_dict | ratings_dict
        data_list.append(data)

    return data_list


def scrape_data():
    page_number = 1
    while True:
        print(f'Scraping from page {page_number}')
        raw_data = get_soup(page_count=page_number, page_size=input_page_size)
        if len(raw_data) == 0:
            print("No more pages to scrap")
            break
        extract_raw_data(raw_data)
        time.sleep(int(input_sleep_time))
        page_number += 1

    df = pd.DataFrame(data_list)
    print(df.shape)
    return df.to_csv(output_data, index=False)


if __name__ == "__main__":
    scrape_data()