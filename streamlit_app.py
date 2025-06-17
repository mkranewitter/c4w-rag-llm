import os
import streamlit as st
from streamlit_feedback import streamlit_feedback
from langsmith import Client
from langchain.callbacks import collect_runs
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

# UI Setup
st.set_page_config(page_title="Kinderbetreuungs-Chatbot", page_icon="🦊")
st.title("🦊 Kinderbetreuungs-Chatbot")

st.markdown("""
Willkommen! Stelle hier deine Fragen zu Kinderbetreuungseinrichtungen in Oberösterreich –
z. B. zu Standorten, Öffnungszeiten oder zur Anmeldung.
""")

# Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_run_id" not in st.session_state:
    st.session_state.last_run_id = None

agent = get_multi_source_agent()

# Hinweistext anzeigen
if not st.session_state.chat_history:
    st.info("👋 Du kannst z. B. fragen: *Welche Einrichtungen gibt es in Hagenberg?*")

# Nutzerfrage
user_input = st.chat_input("Stelle eine Frage…")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append(("user", user_input))

    with st.chat_message("assistant"):
        with st.spinner("Antwort wird generiert..."):
            with collect_runs() as cb:
                try:
                    response = agent(user_input)
                    answer = response.get("output") or response.get("result") or "⚠️ Keine Antwort erhalten."
                except Exception as e:
                    answer = f"❌ Fehler: {str(e)}"

        st.markdown(answer)
        st.session_state.chat_history.append(("assistant", answer))

        run_id = cb.traced_runs[0].id if cb.traced_runs else None
        st.session_state.last_run_id = run_id

# Verlauf + Feedback anzeigen
for i, (role, content) in enumerate(st.session_state.chat_history):
    with st.chat_message(role):
        st.markdown(content)

    # Feedback nach assistant-Antwort anzeigen
    if role == "assistant" and i == len(st.session_state.chat_history) - 1:
        run_id = st.session_state.last_run_id
        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Optional: Was war hilfreich oder unklar?",
            key=f"feedback_{run_id}"
        )

        if feedback and client and run_id:
            emoji = feedback.get("score")
            comment = feedback.get("text", "")
            score_map = {"👍": 1, "👎": 0}
            score = score_map.get(emoji)

            if score is not None:
                try:
                    client.create_feedback(
                        run_id=run_id,
                        feedback_type=f"thumbs {emoji}",
                        score=score,
                        comment=comment or None,
                        feedback_source={"type": "app", "metadata": {"source": "streamlit"}}
                    )
                    st.toast("✅ Danke für dein Feedback!", icon="🦊")
                except Exception as e:
                    st.warning(f"⚠️ Feedback konnte nicht an LangSmith gesendet werden: {e}")