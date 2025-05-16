# scripts/query_rag.py

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from modules.retriever import get_retriever

# Lade Umgebungsvariablen
load_dotenv()

# Lade Retriever (AstraDB + OpenAI Embeddings)
retriever = get_retriever()

# Initialisiere GPT-4o als LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Baue QA-Kette
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Nutzerfrage
question = input("🧠 Was möchtest du wissen? \n> ")

# Antwort generieren
response = qa_chain.invoke({"query": question})

# Ausgabe
print("\n💬 Antwort:")
print(response["result"])

# Optional: Zeige Quellen
print("\n📚 Quellen:")
sources = {doc.metadata.get("source", "Unbekannt") for doc in response["source_documents"]}
for source in sources:
    print("-", source)