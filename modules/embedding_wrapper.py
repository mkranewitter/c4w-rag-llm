# modules/embedding_wrapper.py

from langchain_openai import OpenAIEmbeddings
import os

def get_embedding_model():
    """
    Lädt die OpenAI-Embeddings für die Nutzung im RAG-System.
    """
    return OpenAIEmbeddings(
        model="text-embedding-ada-002", # 
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
