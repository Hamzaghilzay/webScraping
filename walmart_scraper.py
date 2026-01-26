
import requests
from bs4 import BeautifulSoup
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
print(script_tag)
#print(html)

