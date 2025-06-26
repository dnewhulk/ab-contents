# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

BASE_URL = "https://ancabreahna.com"
BLOG_LIST_URL = f"{BASE_URL}/blog/"
DATA_FILE = "blog_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        blog_data = json.load(f)
else:
    blog_data = {}

def get_blog_urls():
    res = requests.get(BLOG_LIST_URL)
    soup = BeautifulSoup(res.content, "html.parser")
    links = soup.select("article a[href*='/blog/']")
    urls = list(set([link["href"] for link in links if link["href"].startswith(BASE_URL)]))
    return urls

def get_blog_links(blog_url):
    res = requests.get(blog_url)
    soup = BeautifulSoup(res.content, "html.parser")
    content_div = soup.find("div", class_="entry-content")
    links = []
    if content_div:
        for a in content_div.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            links.append({"text": text, "href": href})
    return links

def scan_blogs():
    current_urls = get_blog_urls()
    changes = {"new_blogs": [], "updated_links": []}
    
    for url in current_urls:
        blog_id = url.rstrip('/').split('/')[-1]
        links = get_blog_links(url)

        if blog_id not in blog_data:
            blog_data[blog_id] = {
                "url": url,
                "links": links,
                "last_checked": datetime.now().isoformat()
            }
            changes["new_blogs"].append((blog_id, url, links))
        else:
            old_links = blog_data[blog_id]["links"]
            if links != old_links:
                blog_data[blog_id]["links"] = links
                blog_data[blog_id]["last_checked"] = datetime.now().isoformat()
                changes["updated_links"].append((blog_id, url, links))
    
    with open(DATA_FILE, "w") as f:
        json.dump(blog_data, f, indent=2)

    return changes

st.title("📝 Anca Breahna Blog Monitor")
st.write("This tool checks for new blogs or changes in existing blog hyperlinks.")

if st.button("🔍 Run Blog Scan"):
    results = scan_blogs()
    if results["new_blogs"]:
        st.success("✅ New Blogs Found:")
        for blog_id, url, links in results["new_blogs"]:
            st.write(f"- [{blog_id}]({url})")
            for l in links:
                st.write(f"  • [{l['text']}]({l['href']})")
    else:
        st.info("No new blogs found.")

    if results["updated_links"]:
        st.warning("🔁 Blogs with Updated Links:")
        for blog_id, url, links in results["updated_links"]:
            st.write(f"- [{blog_id}]({url})")
            for l in links:
                st.write(f"  • [{l['text']}]({l['href']})")
else:
    st.write("Click the button above to run a scan.")
