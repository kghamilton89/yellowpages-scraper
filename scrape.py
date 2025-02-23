import requests
from lxml import html
import unicodecsv as csv
import argparse
from urllib.parse import quote_plus
import time
import random

# Double the amount of user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def parse_listing(keyword, place, page):
    encoded_place = quote_plus(place)
    url = f"https://www.yellowpages.com/search?search_terms={keyword}&geo_location_terms={encoded_place}&page={page}"

    print("Retrieving ", url)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.yellowpages.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_random_user_agent()
    }

    max_retries = 10
    retry_delay = 5

    for retry in range(max_retries):
        try:
            print(f"Attempt {retry + 1} of {max_retries}")
            response = requests.get(url, verify=True, headers=headers)
            print("Parsing page", page)
            if response.status_code == 200:
                parser = html.fromstring(response.text)

                base_url = "https://www.yellowpages.com"
                parser.make_links_absolute(base_url)

                XPATH_LISTINGS = "//div[@class='search-results organic']//div[@class='v-card']"
                listings = parser.xpath(XPATH_LISTINGS)

                if not listings:
                    print(f"No listings found on page {page}. Exiting.")
                    return []

                scraped_results = []

                for results in listings:
                    XPATH_BUSINESS_NAME = ".//a[@class='business-name']//text()"
                    XPATH_TELEPHONE = ".//div[@class='phones phone primary']//text()"
                    XPATH_ZIP_CODE = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='postalCode']//text()"
                    XPATH_RANK = ".//div[@class='info']//h2[@class='n']/text()"
                    XPATH_WEBSITE = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='links']//a[contains(@class,'website')]/@href"

                    raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
                    raw_business_telephone = results.xpath(XPATH_TELEPHONE)
                    raw_website = results.xpath(XPATH_WEBSITE)
                    raw_zip_code = results.xpath(XPATH_ZIP_CODE)
                    raw_rank = results.xpath(XPATH_RANK)

                    business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                    telephone = ''.join(raw_business_telephone).strip() if raw_business_telephone else None
                    rank = ''.join(raw_rank).replace('.\xa0', '') if raw_rank else None
                    website = ''.join(raw_website).strip() if raw_website else None
                    zipcode = ''.join(raw_zip_code).strip() if raw_zip_code else None

                    business_details = {
                        'business_name': business_name,
                        'telephone': telephone,
                        'rank': rank,
                        'website': website,
                        'zipcode': zipcode,
                    }
                    scraped_results.append(business_details)

                return scraped_results

            elif response.status_code == 404:
                print(f"Could not find a location matching {place}. Status code: 404")
                return []

            else:
                print(f"Failed to process page {page}. Status code: {response.status_code}")
                if retry < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Exiting.")
                    return []

        except Exception as e:
            print(f"Failed to process page {page}: {e}")
            if retry < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.")
                return []

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('keyword', help='Search Keyword')
    argparser.add_argument('place', help='Place Name')
    argparser.add_argument('start_page', type=int, help='Start page number')
    argparser.add_argument('end_page', type=int, help='End page number')

    args = argparser.parse_args()
    keyword = args.keyword.lower()
    place = args.place.lower()
    start_page = args.start_page
    end_page = args.end_page

    all_scraped_data = []

    for page in range(start_page, end_page + 1):
        print(f"Processing page {page}...")
        scraped_data = parse_listing(keyword, place, page)
        if not scraped_data:
            break
        all_scraped_data.extend(scraped_data)

        # Random delay between 10 and 20 seconds
        delay = random.randint(10, 20)
        if page < end_page:
            print(f"Waiting {delay} seconds before processing the next page...")
            time.sleep(delay)

    if all_scraped_data:
        formatted_place = place.replace(", ", "-")
        file_name = f"{keyword}-{formatted_place}-yellowpages.csv"
        print(f"Writing scraped data to {file_name}")
        with open(file_name, 'wb') as csvfile:
            fieldnames = ['rank', 'business_name', 'telephone', 'website', 'zipcode']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in all_scraped_data:
                writer.writerow(data)