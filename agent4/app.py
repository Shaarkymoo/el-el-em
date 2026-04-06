"""
app.py — Streamlit UI for the Digital Forensics Assistant.

Run with:
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="ForensIQ — Digital Forensics Assistant",
    page_icon="🔬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
try:
    from agent import agent, MODEL, MODELS, conversation, _build_system_message
    from tools import list_tools
    import agent as _agent_module
    AGENT_AVAILABLE = True
    _import_error = ""
except ImportError as _ie:
    AGENT_AVAILABLE = False
    _import_error = str(_ie)
    MODEL = "llama3.1:8b"
    MODELS = [MODEL]
    conversation = []
    _agent_module = None

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "chat_display"   not in st.session_state: st.session_state.chat_display   = []
if "selected_model" not in st.session_state: st.session_state.selected_model = MODEL

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🔬 ForensIQ")

    st.subheader("Model")
    if AGENT_AVAILABLE:
        chosen = st.selectbox(
            "Select model",
            options=MODELS,
            index=MODELS.index(st.session_state.selected_model)
                  if st.session_state.selected_model in MODELS else 0,
            label_visibility="collapsed",
        )
        if chosen != st.session_state.selected_model:
            st.session_state.selected_model = chosen
            if _agent_module:
                _agent_module.MODEL = chosen
            st.rerun()
    else:
        st.text(MODEL)

    st.divider()

    st.subheader("Available Tools")
    tool_list = []
    if AGENT_AVAILABLE:
        try:
            tool_list = list_tools()
        except Exception:
            tool_list = []

    if tool_list:
        for t in tool_list:
            st.text(f"▸ {t}")
    else:
        st.warning("No tools found")

    st.divider()

    if st.button("🗑 Clear Conversation", use_container_width=True):
        if AGENT_AVAILABLE:
            conversation.clear()
            conversation.append(_build_system_message())
        st.session_state.chat_display = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("Digital Forensics Assistant")

if not AGENT_AVAILABLE:
    st.error(f"Agent not available: {_import_error}")

# Render chat history
for item in st.session_state.chat_display:
    if item["role"] == "user":
        with st.chat_message("user"):
            st.write(item["text"])
    else:
        with st.chat_message("assistant"):
            steps = item.get("steps", [])
            if steps:
                for step in steps:
                    if step["type"] == "tool_call":
                        args_str = ", ".join(repr(a) for a in step["args"])
                        st.code(f"[tool call]  {step['tool']}({args_str})", language="bash")
                    elif step["type"] == "tool_output":
                        with st.expander("Tool output"):
                            st.code(step["text"], language="text")
            st.write(item.get("final", ""))

# Chat input
user_input = st.chat_input("Enter your forensic query…")

if user_input and user_input.strip():
    st.session_state.chat_display.append({"role": "user", "text": user_input.strip()})

    if not AGENT_AVAILABLE:
        st.session_state.chat_display.append({
            "role": "assistant", "steps": [],
            "final": f"⚠ Agent stack not found — {_import_error}",
        })
        st.rerun()

    with st.spinner("Analysing…"):
        result = agent(user_input.strip())

    st.session_state.chat_display.append({
        "role":  "assistant",
        "steps": result["steps"],
        "final": result["final"],
    })

    st.rerun()