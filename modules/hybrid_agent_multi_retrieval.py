# modules/hybrid_agent_multi_retrieval.py

import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from modules.retriever import get_retriever
from modules.web_search import get_google_search_tool

load_dotenv()

def get_multi_source_agent(callbacks=None):
    # GPT-4o LLM vorbereiten
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        callbacks=callbacks,
    )

    # SQL Agent vorbereiten
    db = SQLDatabase.from_uri(
        os.getenv("POSTGRES_URI"),
        include_tables=["kbbes"],
        sample_rows_in_table_info=3
    )
    sql_agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=False,
        callbacks=callbacks,
    )

    # RAG Retriever vorbereiten
    retriever = get_retriever()
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        callbacks=callbacks,
    )

    # Google Search vorbereiten
    google_search = get_google_search_tool()
    google_search.k = 5  # Mehr als nur 1 Ergebnis holen

    def multi_answer(user_input):
        """
        Führt SQL, RAG und Websuche aus und gibt alles an GPT zur Bewertung und Antwort weiter.
        """
        print("🔍 SQL-Agent wird abgefragt...")
        sql_hint = (
            "Hinweis: Wenn du SQL-Queries erzeugst, verwende bei textuellen Feldern wie ort, name oder art "
            "ILIKE mit Wildcards (z. B. ILIKE '%hagenberg%'). Berücksichtige Umlaute als ae/oe/ue.")
        sql_result = sql_agent.invoke({"input": sql_hint + "\n\n" + user_input}).get("output", "[keine SQL-Antwort]")

        print("📄 RAG (PDF) wird abgefragt...")
        rag_raw = rag_chain.invoke({"query": user_input})
        rag_result = rag_raw.get("result", "[keine RAG-Antwort]")
        rag_sources = rag_raw.get("source_documents", [])

        print("🌍 Google Websuche wird ausgeführt...")
        web_snippets = google_search.results(user_input, num_results=5)
        web_result = "\n\n".join([
            f"{i+1}. {r['snippet']}\nQuelle: {r['link']}" for i, r in enumerate(web_snippets)
        ])

        print("🧠 GPT-4o fasst alle Ergebnisse zusammen...")
        merged_prompt = f"""
Du bist der offizielle Chatbot für Kinderbetreuung in Oberösterreich.
Bitte beantworte die folgende Nutzerfrage basierend auf mehreren Quellen:

Frage:
{user_input}

SQL-Antwort:
{sql_result}

Antwort aus Dokumenten (RAG):
{rag_result}

Ergebnisse aus der Websuche (mit Quellen):
{web_result}

Wichtige Hinweise:
- Antworte nur für Oberösterreich oder Österreich, nicht für andere Länder.
- Verwende einen klaren, verlässlichen und bürgernahen Ton.
- Wenn du keine konkrete Information findest (z. B. Name der Leitung), empfehle einen Kontaktweg (Telefon, E-Mail).
- Formuliere verständlich und direkt. Keine „vielleicht“-Sätze, keine Spekulation.

Bitte kombiniere die Informationen sinnvoll. Wenn etwas mehrfach vorkommt oder sich widerspricht, erwähne das. Wenn eine Quelle besonders relevant ist, gib sie an.
"""

        final = llm.invoke(merged_prompt)
        return {"result": final.content}

    return multi_answer