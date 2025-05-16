# scripts/query_sql_agent.py

from modules.sql_agent import get_sql_agent

agent = get_sql_agent()

# Fuzzy-Hinweis für GPT
fuzzy_hint = (
    "Hinweis: Wenn du SQL-Queries erzeugst, verwende bei textbasierten Feldern wie ort, name oder art "
    "immer ILIKE mit Wildcards (z. B. ILIKE '%hagenberg%'). "
    "Berücksichtige Schreibfehler, Umlaute (ae/oe/ue) und Ortsvarianten.\n\n"
)

while True:
    query = input("💬 Frage an die SQL-Datenbank (oder 'exit'):\n> ")
    if query.lower() in ["exit", "quit"]:
        break

    # Eingabe intern erweitern
    full_prompt = fuzzy_hint + query

    try:
        response = agent.invoke({"input": full_prompt})
        print("✅ Antwort:\n", response)
    except Exception as e:
        print("❌ Fehler:", e)
