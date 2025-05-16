# scripts/test_web_search.py

import os
from dotenv import load_dotenv
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper

load_dotenv()

search = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_cse_id=os.getenv("GOOGLE_CSE_ID")
)

query = "Wie lautet die Telefonnummer des Kindergartens Hagenberg"
print(f"🔍 Suche nach: {query}")
result = search.run(query)

print("\n📄 Ergebnis:")
print(result)