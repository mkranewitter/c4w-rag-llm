# modules/retriever.py

from modules.embedding_wrapper import get_embedding_model
from langchain_astradb import AstraDBVectorStore
import os

def get_retriever():
    """
    Erstellt einen Retriever, der mit OpenAI-Embeddings auf AstraDB basiert.
    """

    # Embedding-Modell laden
    embeddings = get_embedding_model()

    # AstraDB-Details aus Umgebungsvariablen
    astra_db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    astra_db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    astra_db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")
    astra_db_collection_name = os.getenv("ASTRA_DB_COLLECTION_NAME")

    # Verbindung zur AstraDB Vektordatenbank (neue Version)
    vectorstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name=astra_db_collection_name,
        api_endpoint=astra_db_api_endpoint,
        token=astra_db_application_token,
        namespace=astra_db_keyspace
    )

    retriever = vectorstore.as_retriever()

    return retriever