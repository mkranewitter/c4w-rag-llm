import streamlit as st
from modules.hybrid_agent_multi_retrieval import get_multi_source_agent

st.set_page_config(page_title="Kinderbetreuungs-Chatbot", page_icon="🦊")
st.title("🦊 Kinderbetreuungs-Chatbot")

st.markdown("""
Willkommen! Stelle hier deine Fragen zu Kinderbetreuungseinrichtungen in Oberösterreich –
z. B. zu Standorten, Öffnungszeiten oder zur Anmeldung.
""")

# Optional: Fuchsbild einbinden (falls vorhanden)
# st.sidebar.image("assets/Chatbot_LEO.png", caption="Dein Kita-Chat-Fuchs", use_column_width=True)

# Initialisiere den hybriden Agenten
agent = get_multi_source_agent()

# Session State für Verlauf initialisieren
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 👉 Hinweistext anzeigen, solange keine Eingabe gemacht wurde
if not st.session_state.chat_history:
    st.info("👋 Du kannst z. B. fragen: *Welche Einrichtungen gibt es in Hagenberg?*")

# Nutzerinput
user_input = st.chat_input("Stelle eine Frage…")

if user_input:
    # Chatverlauf aktualisieren
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Antwort wird generiert..."):
        try:
            response = agent(user_input)
            if "output" in response:
                answer = response["output"]
            elif "result" in response:
                answer = response["result"]
            else:
                answer = "⚠️ Keine Antwort erhalten."
        except Exception as e:
            answer = f"❌ Fehler: {str(e)}"

    # Antwort speichern und anzeigen
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

# Chatverlauf anzeigen
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])