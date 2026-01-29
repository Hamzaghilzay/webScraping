import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError
from bs4 import BeautifulSoup
import json
import os
import time
import queue

BASE_URL = "https://www.walmart.com"
OUTPUT_FILE = "product_info.json"

HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

product_queue = queue.Queue()
seen_url = set()

def get_product_links_from_search_page(quer, page_number):
    search_url = f"https://www.walmart.com/search?q={query}&page={page_number}"
    max_retries = 5
    backoff_factor = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(search_url, headers = HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            product_links = []

            found = False
            for a_tag in soup.find_all('a', href=True):
                if '/ip/' in a_tag['href']:
                    found = True
                    if "https" in a_tag['href']:
                        full_url = a_tag['href']
                    else:
                        full_url = BASE_URL + a_tag['href']

                    if full_url not in seen_urls:
                        product_links.append(full_url)
            if not found:
                print("\n\n\nSOUP WHEN NOT FOUND", soup)

            return product_links
        except (ConnectionError, Timeout) as e:
            # This handles Wi-Fi blips, DNS issues, or slow responses
            wait_time = backoff_factor ** attempt
            print(f"Connection issue: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

        except HTTPError as e:
            # 412 is Walmart's way of saying "I know you're a bot"
            if e.response.status_code == 412:
                print(f"Precondition Failed (412): Skipping URL.")
                break 
            
            # For other errors like 500 (Server Error), we wait and retry
            wait_time = backoff_factor ** attempt
            print(f"HTTP error {e.response.status_code}. Retrying...")
            time.sleep(wait_time)

        except Exception as e:
            # The "Emergency Brake": Catches everything else so the script doesn't die
            print(f"Unexpected error: {e}")
            break
def extract_product_info(product_url):
    print("Processing URL", product_url)
    max_retries = 5
    backoff_factor = 3
    for attempt in range(max_retries):
        try:
            response = response.get(product_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            script_tag = soup.find('script', id='__NEXT_DATA__')

            if script_tag is None:
                return None


            data = json.loads(script_tag.string)
            def product_info(data):
                        initial_data = data["props"]["pageProps"]["initialData"]["data"]
                        product_data = initial_data["product"]
                        reviews_data = initial_data.get("reviews", {})

            product_info = {
                "price": product_data["priceInfo"]["currentPrice"]["price"],
                "review_count": reviews_data.get("totalReviewCount", 0),
                "item_id": product_data["usItemId"],
                "avg_rating": reviews_data.get("averageOverallRating", 0),
                "product_name": product_data["name"],
                "brand": product_data.get("brand", ""),
                "availability": product_data["availabilityStatus"],
                "image_url": product_data["imageInfo"]["thumbnailUrl"],
                "short_description": product_data.get("shortDescription", "")
            }

            return product_info
        except (ConnectionError, Timeout) as e:
            # This handles Wi-Fi blips, DNS issues, or slow responses
            wait_time = backoff_factor ** attempt
            print(f"Connection issue: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

        except HTTPError as e:
            # 412 is Walmart's way of saying "I know you're a bot"
            if e.response.status_code == 412:
                print(f"Precondition Failed (412): Skipping URL.")
                break 
            
            # For other errors like 500 (Server Error), we wait and retry
            wait_time = backoff_factor ** attempt
            print(f"HTTP error {e.response.status_code}. Retrying...")
            time.sleep(wait_time)

        except Exception as e:
            # The "Emergency Brake": Catches everything else so the script doesn't die
            print(f"Unexpected error: {e}")
            break
def main():
    target_query = "monitor"
    print(f"\n\nSTARTING SCRAPE FOR: {target_query}\n\n")
    with open("OUTPUT_FILE.txt", "w") as file:
        page_number = 1

        while True:
            print(f"---Fetching Page {page_number} ---")
            product_links = get_product_links_from_search_page(target_query, page_number)
            if not product_links or page_number > 100:
                break
            for link in product_links:
                if link not in seen_urls:
                    product_queue.put(link)
                    seen_urls.add(link)

            while not product_queue.empty():
                product_url = product_queue.get()
                product_info = extract_product_info(product_url)
                if product_info:
                    file.write(json.dumps(product_info) + "\n")
                    file.flush() # Forces the data to save to disk immediately

            page_number += 1
if __name__ == "__main__":
    main()
