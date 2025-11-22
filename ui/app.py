# ui/chat.py

import streamlit as st
import requests
import re  # NEW

API_URL = "http://localhost:8000/ask"
API_BASE = "http://localhost:8000"    # NEW

st.set_page_config(page_title="ChatRAG", layout="centered")

# ===============================
# 🎯 PAGE SELECTOR (NEW SECTION)
# ===============================
page = st.sidebar.radio("📌 Select Page", ["Chat", "Logs Viewer"])


# ===============================
# 🧠 PAGE 1: CHAT (EXISTING CODE)
# ===============================
if page == "Chat":
    st.title("🧠 ChatRAG")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    query = st.chat_input("Ask anything...")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})

        with st.spinner("Thinking..."):
            res = requests.post(API_URL, params={"query": query})
            answer = res.json().get(
                "response", "No answer") if res.status_code == 200 else f"Error: {res.text}"

        st.session_state.messages.append(
            {"role": "assistant", "content": answer})
        st.rerun()


# =====================================
# 📄 PAGE 2: LOG VIEWER  (NEW SECTION)
# =====================================
else:
    st.title("📄 Logs Viewer")

    # 🔃 Auto-refresh every 30 seconds
    from streamlit.runtime.scriptrunner import add_script_run_ctx
    st_autorefresh = st.rerun  # optional use below

    # ---- Fetch log files ----
    @st.cache_data(ttl=30)  # auto-refresh list every 30s
    def get_log_files():
        try:
            res = requests.get(f"{API_BASE}/logs")
            if res.status_code == 200:
                files = res.json().get("files", [])
                return sorted(files, reverse=True)
            else:
                return []
        except:
            return []

    # 🔁 Refresh Button
    if st.button("🔄 Refresh Log List"):
        st.cache_data.clear()  # clears cache
        st.rerun()

    files = get_log_files()
    if not files:
        st.warning("No log files found.")
        st.stop()

    # ---- Sidebar File selector ----
    selected_file = st.sidebar.selectbox("📁 Select Log File", files)

    # ---- Fetch content ----
    def fetch_log_content(filename):
        res = requests.get(f"{API_BASE}/logs/{filename}")
        if res.status_code == 200:
            return res.json().get("content", "")
        return f"Error: {res.text}"

    log_content = fetch_log_content(selected_file)

    # ---- Search ----
    search_query = st.text_input("🔍 Search Logs")
    if search_query:
        matches = re.findall(
            rf".*{re.escape(search_query)}.*", log_content, re.IGNORECASE)
        st.write(f"🔎 **Found `{len(matches)}` matches**")
        display_text = "\n".join(matches) if matches else "⚠ No results."
    else:
        display_text = log_content

    # ---- Stats ----
    lines = log_content.split("\n")
    error_count = sum(1 for line in lines if "| ERROR |" in line.lower())
    warn_count = sum(1 for line in lines if "| WARNING|" in line.lower())

    st.subheader("📊 Statistics")
    st.write(f"- **Total lines:** {len(lines)}")
    st.write(f"- **Errors found:** {error_count}")
    st.write(f"- **Warnings found:** {warn_count}")

    # ---- Display ----
    st.subheader(f"📜 Viewing `{selected_file}`")
    st.code(display_text, language="text")

    # ---- Auto bottom scroll ----
    scroll_js = """
    <script>
        window.scrollTo(0, document.body.scrollHeight);
    </script>
    """
    st.components.v1.html(scroll_js, height=0)
