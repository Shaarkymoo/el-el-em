import streamlit as st
from test2 import agent

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Digital Forensics Assistant",
    layout="centered",
)

# ---------------- Soft Aesthetic CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #181818;
    color: #E6E6E6;
}

.chat-wrapper {
    max-width: 720px;
    margin: auto;
    padding-top: 20px;
}

.user {
    background: #2A2A2A;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: right;
    line-height: 1.6;
}

.bot {
    background: #1F1F1F;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: left;
    line-height: 1.6;
}

input {
    background-color: #1F1F1F !important;
    color: #E6E6E6 !important;
    border-radius: 12px !important;
}

textarea {
    background-color: #1F1F1F !important;
    color: #E6E6E6 !important;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- Title ----------------
st.markdown(
    "<h3 style='text-align:center; font-weight:500;'>🧠 Digital Forensics Assistant</h3>",
    unsafe_allow_html=True
)

# ---------------- Chat Area ----------------
st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot'>{msg['content']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Input ----------------
user_input = st.text_input(
    "",
    placeholder="Ask a forensic question or run a tool…",
    label_visibility="collapsed"
)

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.spinner("Thinking…"):
        response = agent(user_input)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    st.rerun()