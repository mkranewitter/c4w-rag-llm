# streamlit_app.py

import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
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
    pd.DataFrame(columns=["timestamp", "question", "answer", "rating", "comment"])\
      .to_csv(FEEDBACK_CSV, index=False)

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

        form_id = str(uuid.uuid4())
        with st.form(form_id):
            st.markdown("📝 Wie hilfreich war diese Antwort?")
            rating = st.radio("Bewertung:", ("👍", "👎"), horizontal=True, key=f"rating_{form_id}")
            comment = st.text_input("Optionaler Kommentar:", key=f"comment_{form_id}")
            submitted = st.form_submit_button("Feedback absenden")
            if submitted:
                feedback_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "question": user_msg,
                    "answer": bot_msg,
                    "rating": "positiv" if rating == "👍" else "negativ",
                    "comment": comment
                }
                pd.DataFrame([feedback_entry]).to_csv(FEEDBACK_CSV, mode="a", header=False, index=False)
                st.success("✅ Danke für dein Feedback!")