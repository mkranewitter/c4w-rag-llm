import os
from uuid import uuid4

import streamlit as st
from langsmith import Client
from langsmith.run_helpers import traceable  # Für Tracing
from streamlit_feedback import streamlit_feedback

from modules.hybrid_agent_multi_retrieval import get_multi_source_agent

# LangSmith configuration from Streamlit secrets
if "LANGCHAIN_API_KEY" in st.secrets and "LANGCHAIN_PROJECT" in st.secrets:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]  # Fixed typo (PROJECT)
    client = Client()
else:
    st.warning("⚠️ LangSmith nicht aktiviert – kein Feedback-Tracking aktiv.")
    client = None

# Page configuration
st.set_page_config(page_title="Kinderbetreuungs-Chatbot", page_icon="🦊")
st.title("🦊 Kinderbetreuungs-Chatbot")

st.markdown(
    """
Willkommen! Stelle hier deine Fragen zu Kinderbetreuungseinrichtungen in Oberösterreich –
z. B. zu Standorten, Öffnungszeiten oder zur Anmeldung.
"""
)

# Create or reuse agent
if "agent" not in st.session_state:
    st.session_state.agent = get_multi_source_agent()
agent = st.session_state.agent

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.chat_history:
    st.info("👋 Du kannst z. B. fragen: *Welche Einrichtungen gibt es in Hagenberg?*")

# User question
user_input = st.chat_input("Stelle eine Frage…")

if user_input:
    with st.spinner("Antwort wird generiert..."):
        @traceable  # LangSmith tracing decorator
        def get_agent_response(user_input):
            try:
                response = agent(user_input)
                return response.get("output") or response.get("result") or "⚠️ Keine Antwort erhalten."
            except Exception as e:
                return f"❌ Fehler: {str(e)}"
        
        answer = get_agent_response(user_input)
        run_id = str(uuid4())  # Generate unique ID for the run

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.session_state.run_id = run_id

# Display conversation and feedback
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

        run_id = st.session_state.get("run_id")
        if feedback and client and run_id:
            rating = feedback["score"]
            comment = feedback["text"]
            try:
                client.create_feedback(
                    run_id=run_id,
                    key="user_feedback",
                    score=1.0 if rating == "👍" else 0.0,  # Angepasst für streamlit-feedback
                    comment=comment,
                    feedback_source={"type": "app", "metadata": {"source": "streamlit"}}
                )
                st.toast("✅ Danke für dein Feedback!", icon="🦊")
            except Exception as e:
                st.warning(f"⚠️ Feedback konnte nicht an LangSmith gesendet werden: {e}")