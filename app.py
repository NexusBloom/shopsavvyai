import streamlit as st
import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools"))

import re

st.set_page_config(page_title="ShopSavvy AI", page_icon="*", layout="wide")

try:
    from real_scraper import RealScraper
    REAL_MODE = True
except:
    REAL_MODE = False

@st.cache_resource
def get_scraper():
    try:
        return RealScraper()
    except:
        return None

scraper = get_scraper() if REAL_MODE else None

def clean_query(raw):
    if not raw:
        return ""
    query = raw.strip()
    for word in ["in jumia", "from jumia", "on jumia", "jumia",
                 "in kilimall", "from kilimall", "on kilimall", "kilimall"]:
        query = re.sub(word, "", query, flags=re.IGNORECASE)
    query = " ".join(query.split())
    return query if query else raw.strip()

@st.cache_data(ttl=300)
def get_products(query, min_p, max_p):
    if not query or not scraper:
        return []
    try:
        all_p = scraper.search_all(query)
        return [p for p in all_p if min_p <= p["price"] <= max_p]
    except:
        return []

def show_product(p, rank):
    with st.container():
        c1, c2, c3 = st.columns([1, 3, 1])
        with c1:
            img_url = p.get("image", "")
            if img_url and img_url.startswith("http"):
                st.image(img_url, width=120)
            else:
                initial = p.get("name", "X")[0].upper()
                bg = "#fff3e0" if p.get("platform") == "Jumia" else "#e8f5e9"
                st.markdown(f"<div style='width:120px;height:120px;background:{bg};display:flex;align-items:center;justify-content:center;font-size:40px;border-radius:8px;'>{initial}</div>", unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"**{p['name']}**")
            plat = p.get("platform", "")
            if plat == "Jumia":
                st.markdown(":orange[**Jumia**]")
            else:
                st.markdown(":green[**Kilimall**]")
            
            price = p.get("price", 0)
            old = p.get("original_price", price)
            if old > price:
                save = old - price
                discount = int((save / old) * 100) if old > 0 else 0
                st.caption(f"~~KES {old:,}~~ | Save KES {save:,} ({discount}% off)")
            
            url = p.get("url", "")
            if url:
                st.markdown(f"[Buy on {plat}]({url})")
        
        with c3:
            st.markdown(f"### KES {price:,}")
            if rank == 1:
                st.success("CHEAPEST")
            elif rank == 2:
                st.info("2nd")
            elif rank == 3:
                st.info("3rd")
        st.markdown("---")

def main():
    st.title("* ShopSavvy AI")
    st.subheader("Compare prices across Jumia and Kilimall Kenya")
    
    if REAL_MODE and scraper:
        st.success("Live Mode")
    else:
        st.error("Demo Mode")
    
    with st.sidebar:
        st.header("Filters")
        min_p, max_p = st.slider("Price Range (KES)", 0, 500000, (0, 100000), 1000)
        platforms = st.multiselect("Platforms", ["Jumia", "Kilimall"], ["Jumia", "Kilimall"])
        sort_opt = st.selectbox("Sort by", ["Price: Low to High", "Price: High to Low"])
    
    st.markdown("### What are you looking for?")
    
    if "search_text" not in st.session_state:
        st.session_state.search_text = ""
    if "do_search" not in st.session_state:
        st.session_state.do_search = False
    
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Search", value=st.session_state.search_text, placeholder="e.g., iphone, headphones...", label_visibility="collapsed")
    with col2:
        search = st.button("Search", use_container_width=True, type="primary")
    
    cols = st.columns(4)
    quick = [("iPhone", "iphone"), ("Headphones", "headphones"), ("Laptop", "laptop"), ("TV", "tv")]
    for col, (label, term) in zip(cols, quick):
        with col:
            if st.button(label, use_container_width=True, key=f"btn_{term}"):
                st.session_state.search_text = term
                st.session_state.do_search = True
                st.rerun()
    
    if st.session_state.do_search:
        search = True
        st.session_state.do_search = False
        query = st.session_state.search_text
    
    if search and query:
        st.markdown("---")
        clean = clean_query(query)
        if not clean:
            st.error("Enter valid search term")
            return
        
        st.info(f"Searching: {clean} | KES {min_p:,} - {max_p:,}")
        
        with st.spinner("Scraping..."):
            products = get_products(clean, min_p, max_p)
            if platforms and products:
                products = [p for p in products if p.get("platform") in platforms]
            
            if sort_opt == "Price: Low to High":
                products.sort(key=lambda x: x["price"])
            else:
                products.sort(key=lambda x: x["price"], reverse=True)
        
        if not products:
            st.error("No products found!")
        else:
            jumia_c = len([p for p in products if p.get("platform") == "Jumia"])
            kilimall_c = len([p for p in products if p.get("platform") == "Kilimall"])
            st.success(f"Found {len(products)} products! (Jumia: {jumia_c}, Kilimall: {kilimall_c})")
            
            cheap = min(products, key=lambda x: x["price"])
            pricey = max(products, key=lambda x: x["price"])
            avg = sum(p["price"] for p in products) / len(products)
            
            sc = st.columns(4)
            sc[0].metric("Total", len(products))
            sc[1].metric("Cheapest", f"KES {cheap['price']:,}")
            sc[2].metric("Average", f"KES {int(avg):,}")
            sc[3].metric("Premium", f"KES {pricey['price']:,}")
            
            st.markdown("---")
            st.subheader("Results")
            
            for i, p in enumerate(products[:20], 1):
                show_product(p, i)
            
            if len(products) > 1:
                st.markdown("---")
                st.subheader("Price Chart")
                chart = {"Product": [f"{p['platform'][:3]}: {p['name'][:10]}..." for p in products[:10]], "Price": [p["price"] for p in products[:10]]}
                st.bar_chart(chart, x="Product", y="Price")

if __name__ == "__main__":
    main()