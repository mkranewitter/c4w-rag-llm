import os
# LangSmith-Konfiguration
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

import streamlit as st
import pandas as pd
from datetime import datetime
from uuid import uuid4
from streamlit_feedback import streamlit_feedback
from modules.hybrid_agent_multi_retrieval import get_multi_source_agent


st.set_page_config(page_title="Kinderbetreuungs-Chatbot", page_icon="🦊")
st.title("🦊 Kinderbetreuungs-Chatbot")

st.markdown("""
Willkommen! Stelle hier deine Fragen zu Kinderbetreuungseinrichtungen in Oberösterreich –
z. B. zu Standorten, Öffnungszeiten oder zur Anmeldung.
""")

# Optional: Fuchsbild einbinden (falls vorhanden)
# st.sidebar.image("assets/Chatbot_LEO.png", caption="Dein Kita-Chat-Fuchs", use_column_width=True)

agent = get_multi_source_agent()

# Session State für Verlauf initialisieren
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Feedback CSV initialisieren
FEEDBACK_CSV = "feedback.csv"
if not os.path.exists(FEEDBACK_CSV):
    pd.DataFrame(columns=["timestamp", "question", "answer", "rating", "comment"]).to_csv(FEEDBACK_CSV, index=False)

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

        # Neue Feedback-Komponente anzeigen
        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Was war hilfreich oder unklar?",
            key=f"feedback_{i}"
        )

        if feedback:
            rating = feedback["score"]
            comment = feedback["text"]
            entry = {
                "timestamp": datetime.now().isoformat(),
                "question": user_msg,
                "answer": bot_msg,
                "rating": "positiv" if rating == 1 else "negativ",
                "comment": comment
            }
            pd.DataFrame([entry]).to_csv(FEEDBACK_CSV, mode="a", header=False, index=False)
            st.toast("✅ Danke für dein Feedback!", icon="🦊")