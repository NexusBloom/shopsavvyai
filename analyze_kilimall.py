import requests
from bs4 import BeautifulSoup
import re

url = "https://www.kilimall.co.ke/search?q=headphones"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print(f"Fetching: {url}")
r = requests.get(url, headers=headers, timeout=20)
print(f"Status: {r.status_code}")

soup = BeautifulSoup(r.content, "lxml")

# Look for image patterns in the HTML
print("\n=== Looking for image URLs ===")
img_patterns = ['.jpg', '.jpeg', '.png', '.webp', 'cdn.', 'img.', 'image']
html_text = str(soup)

# Find all URLs that look like images
potential_images = re.findall(r'https?://[^\s"<>]+?\.(?:jpg|jpeg|png|webp)', html_text)
print(f"Found {len(potential_images)} potential image URLs")
for img in potential_images[:5]:
    print(f"  {img[:80]}")

# Look for data attributes that might contain images
print("\n=== Looking for data attributes ===")
data_attrs = re.findall(r'data-[a-z-]+=["\']?(https?://[^"\']+)["\']?', html_text)
print(f"Found {len(data_attrs)} URLs in data attributes")
for attr in data_attrs[:5]:
    print(f"  {attr[:80]}")

# Look for JSON data that might contain images
print("\n=== Looking for JSON/image data ===")
json_patterns = re.findall(r'"image["\']?\s*:\s*["\']?(https?://[^"\']+)["\']?', html_text)
print(f"Found {len(json_patterns)} image URLs in JSON-like data")
for p in json_patterns[:5]:
    print(f"  {p[:80]}")

# Check specific product containers
print("\n=== Checking product containers ===")
products = soup.find_all("div", class_=re.compile(r"product|item|goods"))
print(f"Found {len(products)} product containers")

if products:
    first = products[0]
    print(f"\nFirst product HTML structure:")
    print(first.prettify()[:1000])
    
    # Look for any img tags
    imgs = first.find_all("img")
    print(f"\nFound {len(imgs)} img tags in first product")
    for i, img in enumerate(imgs):
        print(f"  Img {i}: {img}")
        for attr in img.attrs:
            print(f"    {attr}: {str(img[attr])[:60]}")

# Save full HTML for inspection
with open("kilimall_page.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())
print("\nSaved full HTML to kilimall_page.html")
