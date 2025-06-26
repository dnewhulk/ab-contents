import streamlit as st
import requests
from bs4 import BeautifulSoup

# URLs
BASE_URL = "https://ancabreahna.com"
BLOG_LIST_URL = f"{BASE_URL}/blog/"

# Set page config
st.set_page_config(page_title="Anca Breahna Blog Monitor", layout="wide")

st.title("📝 Anca Breahna Blog Monitor")
st.caption("Automatically scans the blog for updates and displays blog links + internal hyperlinks from each post.")

@st.cache_data(show_spinner=True)
def get_blog_urls():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(BLOG_LIST_URL, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    links = soup.select("article a[href*='/blog/']")
    urls = list(set([link["href"] for link in links if link["href"].startswith(BASE_URL)]))
    return urls

@st.cache_data(show_spinner=True)
def get_blog_links(blog_url):
    res = requests.get(blog_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.content, "html.parser")
    content_div = soup.find("div", class_="entry-content")
    links = []
    if content_div:
        for a in content_div.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if href.startswith("http"):
                links.append({"text": text, "href": href})
    return links


# --- Main App Logic ---

blog_urls = get_blog_urls()

if not blog_urls:
    st.warning("No blogs found on the site.")
else:
    st.success(f"✅ Found {len(blog_urls)} blog post(s).")
    
    for i, url in enumerate(sorted(blog_urls), 1):
        blog_slug = url.rstrip("/").split("/")[-1]
        with st.expander(f"{i}. [{blog_slug}]({url})", expanded=False):
            st.markdown(f"🔗 **Blog URL**: [{url}]({url})", unsafe_allow_html=True)
            links = get_blog_links(url)
            if links:
                st.markdown("### Internal Hyperlinks in Content:")
                for link in links:
                    st.markdown(f"- [{link['text']}]({link['href']})")
            else:
                st.info("No internal hyperlinks found in this blog.")
