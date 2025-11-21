# ui/chat.py

import streamlit as st
import requests

API_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="ChatRAG", layout="centered")
st.title("🧠 ChatRAG")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages in a container
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

# --- IMPORTANT: input must be OUTSIDE container ---
query = st.chat_input("Ask anything...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Thinking..."):
        res = requests.post(API_URL, params={"query": query})

        answer = res.json().get(
            "response", "No answer") if res.status_code == 200 else f"Error: {res.text}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()    # Refresh to keep input at bottom
