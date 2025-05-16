# scripts/query_hybrid.py

from modules.hybrid_agent_improved import get_hybrid_agent

# Initialisiere hybriden Agent (SQL + RAG)
agent = get_hybrid_agent()

while True:
    query = input("💬 Frage an das hybride System (oder 'exit'):\n> ")
    if query.lower() in ["exit", "quit"]:
        break

    try:
        response = agent(query)
        # SQL-Antworten enthalten 'output', RAG-Antworten 'result'
        if "output" in response:
            print("✅ Antwort:\n", response["output"])
        elif "result" in response:
            print("✅ Antwort:\n", response["result"])
        else:
            print("⚠️ Keine Antwort erhalten.")
    except Exception as e:
        print("❌ Fehler:", e)
