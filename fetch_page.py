import requests
from bs4 import BeautifulSoup
import re

url = "https://www.yes24.com/product/category/bestseller?categoryNumber=001001003&pageNumber=1&pageSize=24"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.yes24.com/"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("=== Searching for common yes24 list structures ===")
    
    # Save the HTML to temp_page.html
    with open("temp_page.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print("Saved HTML to temp_page.html")
    
except Exception as e:
    print(f"Error occurred: {e}")
