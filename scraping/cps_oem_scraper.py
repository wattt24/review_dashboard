# scraping/cps_oem_scraper.py

import streamlit as st
import requests
 

def fetch_posts(per_page=10):
 
    url = "https://www.cpsmanu.com/wp-json/wp/v2/posts"
    params = {
        "per_page": per_page,
        "orderby": "date",
        "order": "desc"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching posts: {e}")
        return []
