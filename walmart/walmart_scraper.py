import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError
from bs4 import BeautifulSoup
import json
import os
import time
import queue
import random

# ==========================================
# 1. CONFIGURATION & IDENTITY
# ==========================================
BASE_URL = "https://www.walmart.com"
OUTPUT_FILE = "product_info.jsonl" # .jsonl is better for scraping; one JSON object per line

# Headers make your script look like a real browser. 
# Without these, websites see "Python-Requests" and block you instantly.
HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "referer": "https://www.google.com/" # "Referer" tells the site you came from Google
}

# Use a Session to persist cookies (like a real browser tab)
session = requests.Session() 
session.headers.update(HEADERS)

# ==========================================
# 2. STATE MANAGEMENT
# ==========================================
# The Queue stores links we find but haven't visited yet
product_queue = queue.Queue()
# seen_urls prevents us from scraping the same product twice
seen_urls = set()

async def get_product_links_from_search_page(query, page_number):
    async with Stealth().use_async(async_palywright()) as p:
        # 1. Launc a real browser (headless = False lets you watch it work!)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_page()
        #2. Apply the stealth plugin
        #await stealth_async(context)
        #3. Go to the URL
        search_url = f"https://www.walmart.com/search?q={query}&page={page_number}"
        print(f"Opening: {search_url}")

        try:
            await context.goto(search_url, wait_until="networkidle")

            #4. Human behaviour: Scroll down slowly
            await context.evaluate("window.scrollTo(0, document.body.scrollHeight /2)")
            await asyncio.sleep(2)

            #5. Grab th HTML and find links
            html = await context.content()
            soup = BeautifulSoup(html, 'lxml')

            product_links = []
            found = False

            # Search the HTML for all <a> tags (links)
            for a_tag in soup.find_all('a', href=True):
                # '/ip/' is Walmart's internal code for an "Item Page"
                if '/ip/' in a_tag['href']:
                    found = True
                    # Clean the URL to make sure it's a full link
                    if "https" in a_tag['href']:
                        full_url = a_tag['href']
                    else:
                        full_url = BASE_URL + a_tag['href']

                    if full_url not in seen_urls:
                        product_links.append(full_url('?')[0])
            
            if not found:
                print(f"Warning: No links found on page {page_number}. Might be a block.")
            await browser.close()
            return product_links

        except Exception as e:
            print(f"Playwright error: {e}")
            await browser.close()
            return []

def extract_product_info(product_url):
    """
    Visits a specific product page and extracts price, rating, and name.
    """
    print(f"Extracting: {product_url}")
    max_retries = 5
    backoff_factor = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.get(product_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Walmart stores its data in a hidden JSON object inside a <script> tag.
            # This is much faster and cleaner than scraping the visible text!
            script_tag = soup.find('script', id='__NEXT_DATA__')
            if script_tag is None:
                return None

            # Parse that hidden JSON into a Python dictionary
            data = json.loads(script_tag.string)
            initial_data = data["props"]["pageProps"]["initialData"]["data"]
            product_data = initial_data["product"]
            reviews_data = initial_data.get("reviews", {})

            # Map the JSON data to our own cleaner dictionary
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

        except Exception as e:
            wait_time = backoff_factor ** attempt
            print(f"Error on product page: {e}. Retrying...")
            time.sleep(wait_time)

# ==========================================
# 3. MAIN ORCHESTRATION LOOP
# ==========================================
def main():
    target_query = "monitor"
    print(f"\nSTARTING SCRAPE FOR: {target_query}\n")
    
    with open(OUTPUT_FILE, "w") as file:
        page_number = 1

        while True:
            # STEP 1: Get links from a search page
            print(f"--- Fetching Search Page {page_number} ---")
            product_links = get_product_links_from_search_page(target_query, page_number)
            
            # HUMAN DELAY: Wait between search pages
            wait_time = random.uniform(15, 45)
            print(f"Human Pause: Waiting {wait_time:.2f}s before moving forward...")
            time.sleep(wait_time)

            # STOPPING CONDITIONS: No links found or we reached the limit
            if not product_links or page_number > 100:
                print("No more links or limit reached. Finishing.")
                break

            # STEP 2: Add links to the "To-Do List" (Queue)
            for link in product_links:
                if link not in seen_urls:
                    product_queue.put(link)
                    seen_urls.add(link)

            # STEP 3: Process the "To-Do List"
            while not product_queue.empty():
                product_url = product_queue.get()
                product_info = extract_product_info(product_url)
                
                if product_info:
                    # Write immediately to file so we don't lose data if the script crashes
                    file.write(json.dumps(product_info) + "\n")
                    file.flush() 
                    
                # HUMAN DELAY: Wait between individual products
                product_pause = random.uniform(5, 12)
                time.sleep(product_pause)
            
            page_number += 1

if __name__ == "__main__":
    main()
