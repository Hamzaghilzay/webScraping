import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

import requests, certifi
from bs4 import BeautifulSoup
url = "https://www.timesjobs.com/job-detail/sme-terraform-python-jenkins-hcl-technologies-remote-5-10-years-jobid-K6JNZV8elWFzpSvf+uAgZw==&source=srp"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

html = requests.get(url, headers = headers, verify = False).text
soup = BeautifulSoup(html, "lxml")
job = soup.find("h1", class_ = "text-lg font-bold").text
print(job)
