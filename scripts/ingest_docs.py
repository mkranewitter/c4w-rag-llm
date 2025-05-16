# scripts/ingest_docs.py

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore

# Umgebungsvariablen laden
load_dotenv()

# OpenAI Embeddings vorbereiten
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# AstraDB Konfiguration vorbereiten
vectorstore = AstraDBVectorStore(
    embedding=embeddings,
    collection_name=os.getenv("ASTRA_DB_COLLECTION_NAME"),
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    namespace=os.getenv("ASTRA_DB_KEYSPACE"),
)

# Speicherort der Quelldateien
source_dir = Path("data/knowledge_base")
text_files = list(source_dir.glob("*.txt"))

# Textsplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

all_chunks = []

# Lade und splitte alle Dateien
for file in text_files:
    print(f"📄 Lade Datei: {file.name}")
    loader = TextLoader(str(file), encoding="utf-8")
    docs = loader.load()
    chunks = splitter.split_documents(docs)
    all_chunks.extend(chunks)

# Upload in AstraDB
print(f"🚀 Hochladen von {len(all_chunks)} Chunks in Collection: {os.getenv('ASTRA_DB_COLLECTION_NAME')}")
vectorstore.add_documents(all_chunks)
print("✅ Upload abgeschlossen.")