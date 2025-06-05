import os
import streamlit as st
from datetime import datetime
from uuid import uuid4
from streamlit_feedback import streamlit_feedback
from langsmith import Client
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler
from modules.hybrid_agent_multi_retrieval import get_multi_source_agent

# LangSmith-Konfiguration
if "LANGCHAIN_API_KEY" in st.secrets and "LANGCHAIN_PROJECT" in st.secrets:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]
    client = Client()
else:
    st.warning("⚠️ LangSmith nicht aktiviert – kein Feedback-Tracking aktiv.")
    client = None

# Streamlit Setup
st.set_page_config(page_title="Kinderbetreuungs-Chatbot", page_icon="🦊")
st.title("🦊 Kinderbetreuungs-Chatbot")

st.markdown("""
Willkommen! Stelle hier deine Fragen zu Kinderbetreuungseinrichtungen in Oberösterreich –
z. B. zu Standorten, Öffnungszeiten oder zur Anmeldung.
""")

# Session State initialisieren
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "run_ids" not in st.session_state:
    st.session_state.run_ids = []

# Agent mit Callback vorbereiten
run_collector = RunCollectorCallbackHandler()
agent = get_multi_source_agent(callbacks=[run_collector])

# Nutzerfrage eingeben
user_input = st.chat_input("Stelle eine Frage…")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    with st.chat_message("assistant"):
        with st.spinner("Antwort wird generiert..."):
            try:
                response = agent(user_input)
                answer = response.get("output") or response.get("result") or "⚠️ Keine Antwort erhalten."
            except Exception as e:
                answer = f"❌ Fehler: {str(e)}"
        st.markdown(answer)

    st.session_state.chat_history.append(("assistant", answer))
    run_id = run_collector.traced_runs[0].id if run_collector.traced_runs else None
    st.session_state.run_ids.append(run_id)

# Chatverlauf & Feedback anzeigen
for i, (role, content) in enumerate(st.session_state.chat_history):
    with st.chat_message(role):
        st.markdown(content)

    if role == "assistant":
        run_id = st.session_state.run_ids[i // 2] if i // 2 < len(st.session_state.run_ids) else None

        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Was war hilfreich oder unklar?",
            key=f"feedback_{i}",
        )

        if feedback and client and run_id:
            try:
                client.create_feedback(
                    run_id=run_id,
                    key="user_feedback",
                    score=1.0 if feedback["score"] == 1 else 0.0,
                    comment=feedback.get("text"),
                    feedback_source={"type": "app", "metadata": {"source": "streamlit"}}
                )
                st.toast("✅ Danke für dein Feedback!", icon="🦊")
            except Exception as e:
                st.warning(f"⚠️ Feedback konnte nicht gesendet werden: {e}")
