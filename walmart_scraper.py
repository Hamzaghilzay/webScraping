import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

url = "https://www.walmart.com/ip/Packard-Bell-airFrame-21-Inch-Monitor-FHD-1920-x-1080-Computer-Dual-Monitor-Ultrawide-Monitor-VESA-Mount-Tilt-VGA-HDMI-Monitor-Basic-Gaming-Monitor/1707857996?adsRedirect=true"
response = requests.get(url, headers = HEADERS)
soup = BeautifulSoup(response.text, "lxml")
script_tag = soup.find("script", id="__NEXT_DATA__")

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
print(product_info(data))
