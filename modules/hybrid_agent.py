# modules/hybrid_agent.py

import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from modules.retriever import get_retriever

# Lade Umgebungsvariablen
load_dotenv()

def get_hybrid_agent():
    # Initialisiere GPT-4o
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # SQL-Datenbank konfigurieren (nur Tabelle 'kbbes')
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

    # RAG-Chain: Retriever + LLM für PDF-Wissen
    retriever = get_retriever()
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    # Routing-Funktion
    def hybrid_answer(user_input):
        """
        Einfaches Keyword-basiertes Routing.
        Der Fuzzy-Hinweis wird nur an den SQL-Agent übergeben.
        """

        # Fuzzy-Hinweis für GPT-4o (nur SQL-Fälle)
        fuzzy_hint = (
            "Hinweis: Wenn du SQL-Queries erzeugst, verwende bei textbasierten Feldern wie ort, name oder art "
            "immer ILIKE mit Wildcards (z. B. ILIKE '%hagenberg%'). "
            "Berücksichtige Schreibfehler, Umlaute (ae/oe/ue) und Ortsvarianten.\n\n"
        )

        # Keywords zur Unterscheidung
        # Schlüsselwörter für SQL-typische Fragen (Einrichtungen, Orte, Öffnungszeiten etc.)
        sql_keywords = [
            "wo", "welche", "einrichtung", "betreuung", "ort", "gemeinde",
            "kindergarten", "krabbelstube", "hort", "kita", "kbbes",

        # Direkt aus Spaltennamen
            "name", "betreiber", "angebot", "art", "betreuungsform", "alter",
            "verfügbarkeit", "zielgruppe", "zielgruppen", "notiz",
            "straße", "strasse", "hausnummer", "plz", "ort", "gemeindenummer",
            "telefon", "email", "web", "website", "url",
            "öffnungszeiten", "schließzeiten", "bezirk", "bezirksnummer",
            "emaildomain", "email-domain"
        ]
        
        # Schlüsselwörter für RAG-typische Fragen (Anmeldung, Ablauf etc.)
        rag_keywords = [
            "anmeldung", "wie funktioniert", "unterlagen", "fristen",
            "förderung", "prozess"
        ]
        
        # Kleinbuchstabenvergleich zur Vereinheitlichung
        input_lc = user_input.lower()

        if any(k in input_lc for k in sql_keywords):
            print("🔍 Routing: SQL-Agent")
            return sql_agent.invoke({"input": fuzzy_hint + user_input})
        elif any(k in input_lc for k in rag_keywords):
            print("📄 Routing: RAG")
            return rag_chain.invoke({"query": user_input})
        else:
            print("🤖 Routing: Default fallback to RAG")
            return rag_chain.invoke({"query": user_input})

    return hybrid_answer
