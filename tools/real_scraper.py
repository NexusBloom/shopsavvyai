import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import quote_plus, urljoin

class RealScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def _clean_price(self, text):
        if not text:
            return 0
        nums = re.sub(r"[^\d]", "", str(text))
        return int(nums) if nums else 0
    
    def _get_jumia(self, query):
        products = []
        try:
            url = f"https://www.jumia.co.ke/catalog/?q={quote_plus(query)}"
            r = self.session.get(url, timeout=20)
            soup = BeautifulSoup(r.content, "lxml")
            items = soup.find_all("article", class_="prd")
            
            for item in items[:15]:
                try:
                    name = item.find("h3", class_="name")
                    price = item.find("div", class_="prc")
                    if not name or not price:
                        continue
                    
                    p = self._clean_price(price.text)
                    if p == 0:
                        continue
                    
                    link = item.find("a", class_="core")
                    href = link.get("href", "") if link else ""
                    
                    old_price_elem = item.find("div", class_="old")
                    old_price = self._clean_price(old_price_elem.text) if old_price_elem else p
                    
                    img = item.find("img")
                    img_url = img.get("data-src", "") or img.get("src", "") if img else ""
                    
                    products.append({
                        "name": name.text.strip(),
                        "price": p,
                        "original_price": old_price if old_price > p else p,
                        "platform": "Jumia",
                        "url": urljoin("https://www.jumia.co.ke", href),
                        "image": img_url
                    })
                except:
                    continue
        except Exception as e:
            print(f"Jumia error: {e}")
        
        return sorted(products, key=lambda x: x["price"])
    
    def _get_kilimall(self, query):
        products = []
        try:
            url = f"https://www.kilimall.co.ke/search?q={quote_plus(query)}"
            r = self.session.get(url, timeout=25)
            soup = BeautifulSoup(r.content, "lxml")
            
            # Look for product links
            links = soup.find_all("a", href=re.compile(r"/product/|/item/|/p/\d+"))
            
            processed = set()
            for link in links[:20]:
                try:
                    href = link.get("href", "")
                    if not href or href in processed:
                        continue
                    processed.add(href)
                    
                    full_url = urljoin("https://www.kilimall.co.ke", href)
                    
                    # Get image
                    img = link.find("img")
                    img_url = ""
                    if img:
                        for attr in ['src', 'data-src', 'data-original', 'data-img']:
                            val = img.get(attr, '')
                            if val and val.startswith('http'):
                                img_url = val
                                break
                            elif val and val.startswith('/'):
                                img_url = "https://www.kilimall.co.ke" + val
                                break
                    
                    # Get name
                    name = ""
                    if img and img.get('alt'):
                        name = img.get('alt')
                    else:
                        name = link.get_text(strip=True)
                    
                    if len(name) < 3:
                        continue
                    
                    # Get price
                    price = 0
                    price_match = re.search(r'KSh[\s]*([\d,]+)', link.get_text())
                    if not price_match and link.parent:
                        price_match = re.search(r'KSh[\s]*([\d,]+)', link.parent.get_text())
                    
                    if price_match:
                        price = self._clean_price(price_match.group(1))
                    
                    if price == 0:
                        continue
                    
                    products.append({
                        "name": name[:100],
                        "price": price,
                        "original_price": price,
                        "platform": "Kilimall",
                        "url": full_url,
                        "image": img_url
                    })
                    
                except:
                    continue
            
        except Exception as e:
            print(f"Kilimall error: {e}")
        
        return sorted(products, key=lambda x: x["price"])
    
    def search_all(self, query, max_results=50):
        all_p = []
        
        jumia = self._get_jumia(query)
        all_p.extend(jumia)
        
        time.sleep(2)
        
        kilimall = self._get_kilimall(query)
        all_p.extend(kilimall)
        
        all_p.sort(key=lambda x: x["price"])
        return all_p[:max_results]