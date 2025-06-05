import os
from langsmith import Client
import streamlit as st
from datetime import datetime
from uuid import uuid4
from streamlit_feedback import streamlit_feedback
from modules.hybrid_agent_multi_retrieval import get_multi_source_agent

# LangSmith-Konfiguration aus Streamlit Secrets
if "LANGCHAIN_API_KEY" in st.secrets and "LANGCHAIN_PROJECT" in st.secrets:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]
    client = Client()
else:
    st.warning("⚠️ LangSmith nicht aktiviert – API Key oder Projektname fehlt.")
    client = None

st.set_page_config(page_title="Kinderbetreuungs-Chatbot", page_icon="🦊")
st.title("🦊 Kinderbetreuungs-Chatbot")

st.markdown("""
Willkommen! Stelle hier deine Fragen zu Kinderbetreuungseinrichtungen in Oberösterreich –
z. B. zu Standorten, Öffnungszeiten oder zur Anmeldung.
""")

agent = get_multi_source_agent()

# Session State für Verlauf initialisieren
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Hinweistext anzeigen, solange keine Eingabe gemacht wurde
if not st.session_state.chat_history:
    st.info("👋 Du kannst z. B. fragen: *Welche Einrichtungen gibt es in Hagenberg?*")

# Nutzerinput
user_input = st.chat_input("Stelle eine Frage…")

if user_input:
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

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

# Chatverlauf + Feedback anzeigen
for i in range(0, len(st.session_state.chat_history), 2):
    user_msg = st.session_state.chat_history[i]["content"]
    bot_msg = st.session_state.chat_history[i + 1]["content"] if i + 1 < len(st.session_state.chat_history) else ""

    with st.chat_message("user"):
        st.markdown(user_msg)
    with st.chat_message("assistant"):
        st.markdown(bot_msg)

        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Was war hilfreich oder unklar?",
            key=f"feedback_{i}"
        )

        if feedback:
            rating = feedback["score"]
            comment = feedback["text"]
            st.toast("✅ Danke für dein Feedback!", icon="🦊")

            # Feedback an LangSmith senden (wenn aktiviert)
            if client:
                try:
                    from langchain.smith import get_traceable_awaitable
                    run = get_traceable_awaitable()
                    if run and run.run_id:
                        client.create_feedback(
                            run_id=run.run_id,
                            key="user_feedback",
                            score=1.0 if rating == 1 else 0.0,
                            comment=comment,
                            feedback_source={"type": "app", "metadata": {"source": "streamlit"}}
                        )
                except Exception as e:
                    st.warning(f"⚠️ Feedback konnte nicht an LangSmith gesendet werden: {e}")
