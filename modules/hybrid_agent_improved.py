# modules/hybrid_agent.py

import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from modules.retriever import get_retriever
from modules.web_search import get_google_search_tool

# Lade Umgebungsvariablen
load_dotenv()

def get_hybrid_agent():
    # Initialisiere GPT-4o
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # SQL-Datenbank konfigurieren
    db = SQLDatabase.from_uri(
        os.getenv("POSTGRES_URI"),
        include_tables=["kbbes"],
        sample_rows_in_table_info=3
    )

    # SQL-Agent erstellen
    sql_agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )

    # RAG-Chain (PDF-Inhalte)
    retriever = get_retriever()
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    # Google Search Wrapper vorbereiten
    google_search = get_google_search_tool()

    def hybrid_answer(user_input):
        """
        Sequentielle Verarbeitung: SQL → RAG → Google (mit GPT-Auswertung)
        """

        fuzzy_hint = (
            "Hinweis: Wenn du SQL-Queries erzeugst, verwende bei textbasierten Feldern wie ort, name oder art "
            "immer ILIKE mit Wildcards (z. B. ILIKE '%hagenberg%'). "
            "Berücksichtige Schreibfehler, Umlaute (ae/oe/ue) und Ortsvarianten.\n\n"
        )

        print("🔍 Versuche SQL-Agent...")
        sql_response = sql_agent.invoke({"input": fuzzy_hint + user_input})
        sql_output = sql_response.get("output", "").lower()

        if sql_response and len(sql_output.strip()) > 20 and not any(
            phrase in sql_output for phrase in [
                "keine einträge", "nicht vorhanden", "nicht in der datenbank",
                "möglicherweise", "keine daten"
            ]):
            return sql_response

        print("📄 Versuche RAG...")
        rag_response = rag_chain.invoke({"query": user_input})
        rag_output = rag_response.get("result", "").lower()

        if rag_response and len(rag_output.strip()) > 20 and rag_response.get("source_documents"):
            return rag_response

        print("🌍 Versuche Google Websuche...")
        web_result = google_search.run(user_input)

        print("🤖 GPT formuliert Antwort basierend auf Websuche...")
        final_response = llm.invoke(
            f"Antworte bitte auf folgende Nutzerfrage basierend auf diesen Google-Suchergebnissen:\n\nFrage: {user_input}\n\nSuchergebnisse:\n{web_result}"
        )
        return {"result": final_response.content}

    return hybrid_answer
