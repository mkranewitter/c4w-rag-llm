# modules/web_search.py

import os
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper

def get_google_search_tool():
    return GoogleSearchAPIWrapper(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID"),
        k=5  # mehrere Ergebnisse holen
    )
