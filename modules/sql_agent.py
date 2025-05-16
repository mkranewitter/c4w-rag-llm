import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

# Umgebungsvariablen laden (.env)
load_dotenv()

def get_sql_agent():
    # Verbindung zur PostgreSQL-Datenbank (nur Tabelle 'kbbes')
    db = SQLDatabase.from_uri(
        os.getenv("POSTGRES_URI"),
        include_tables=["kbbes"],     # nur die relevante Tabelle
        sample_rows_in_table_info=3   # Kontext für das LLM
    )

    # GPT-4o initialisieren
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # SQL-Agent initialisieren (über OpenAI Function Calling)
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )

    return agent