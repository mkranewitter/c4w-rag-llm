# scripts/test_google_search_raw.py

import os
from dotenv import load_dotenv
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper

# .env laden (für GOOGLE_API_KEY und GOOGLE_CSE_ID)
load_dotenv()

# GoogleSearchAPIWrapper initialisieren
search = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_cse_id=os.getenv("GOOGLE_CSE_ID")
)

# Anzahl der Ergebnisse
num_results = 5

while True:
    query = input("🔍 Websuche (oder 'exit'):\n> ")
    if query.lower() in ["exit", "quit"]:
        break

    print("\n🌐 Google-Suchergebnisse (strukturiert):\n")
    try:
        results = search.results(query, num_results=num_results)
        for i, res in enumerate(results):
            print(f"{i+1}. {res['title']}")
            print(f"   {res['snippet']}")
            print(f"   Quelle: {res['link']}\n")
    except Exception as e:
        print(f"❌ Fehler bei der Websuche: {e}")
    
    print("-" * 80 + "\n")
