from modules.hybrid_agent_multi_retrieval import get_multi_source_agent

agent = get_multi_source_agent()

while True:
    query = input("💬 Frage (oder 'exit'):\n> ")
    if query.lower() in ["exit", "quit"]:
        break

    result = agent(query)
    print("\n✅ Antwort:\n", result["result"])
