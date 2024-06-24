import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

data_list = []
def get_soup(page_count=1, page_size=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    url = f"https://www.airlinequality.com/airline-reviews/kenya-airways/page/{page_count}/?sortby=post_date%3ADesc&pagesize={page_size}"
    response = requests.get(url, headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        return soup
    else:
        print("Error in getting soup")


def extract_raw_data(soup):
    # extract the data from the soup
    articles = soup.find_all("article", itemprop="review")

    for article in articles:

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
            trip_verification = re.search(r'(Trip Verified|Not Verified)', trip_verification.text).group(1)
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
            review = review.split('|', 1)[1].strip()
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


if __name__ == "__main__":
    raw_data = get_soup()

    for page_count in range(1, 2):
        print(f'Scraping from page {page_count}')
        extract_raw_data(raw_data)
        # time.sleep(4)

    df = pd.DataFrame(data_list)
    print(df)
    df.to_csv("kenya_airways.csv", index=False)
