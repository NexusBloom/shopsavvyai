from bs4 import BeautifulSoup
import re

with open("kilimall_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

print("=== Looking for product containers ===")

class_names = [
    "product", "item", "goods", "list-item", "product-item", 
    "goods-item", "product-list", "search-item", "result-item"
]

for cls in class_names:
    items = soup.find_all(class_=re.compile(cls, re.I))
    if items:
        print(f"Class '{cls}': {len(items)} items")
        if 0 < len(items) < 50:
            print("Sample item:")
            print(items[0].prettify()[:800])
            break

print("\n=== Looking for product links ===")
links = soup.find_all("a", href=re.compile(r"/product/|/item/|/goods/|/p/"))
print(f"Found {len(links)} product links")
if links:
    for i, link in enumerate(links[:3]):
        print(f"Link {i+1}: {link.get('href', '')}")
        img = link.find("img")
        if img:
            print(f"  Image: {img.get('src', img.get('data-src', 'none'))[:60]}")

print("\n=== Looking for prices ===")
prices = soup.find_all(string=re.compile(r'KSh\s*\d+'))
print(f"Found {len(prices)} price elements")
