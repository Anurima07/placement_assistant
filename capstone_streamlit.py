import streamlit as st
from agent import run_agent
import time

st.set_page_config(page_title="AI Placement Assistant", layout="centered")

# -----------------------------
# DARK MODE SAFE STYLING
# -----------------------------
st.markdown("""
<style>
.chat-bubble-user {
    background-color: #2E7D32;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 8px;
    max-width: 80%;
}

.chat-bubble-ai {
    background-color: #1E1E1E;
    color: white;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 8px;
    max-width: 80%;
}

.chat-container {
    display: flex;
    flex-direction: column;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "1"

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    if st.button("🆕 New Chat"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(int(st.session_state.thread_id) + 1)
        st.rerun()

    st.markdown("---")

    st.markdown("### 📌 Capabilities")
    st.markdown("""
- 📊 Job Match Analysis  
- 📄 Resume Builder  
- 🧠 DSA Roadmap  
- 🎤 HR Prep  
""")

    st.markdown("---")

    st.markdown("### 💡 Try asking:")
    st.markdown("""
- Give me DSA roadmap  
- HR interview mistakes  
- Analyze this JD  
- Create my resume  
""")

# -----------------------------
# HEADER
# -----------------------------
st.markdown("## 🎯 AI Placement Assistant")
st.caption("Smart career guidance powered by AI")

# -----------------------------
# CHAT DISPLAY
# -----------------------------
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"""
<div class="chat-bubble-user">👤 {chat["content"]}</div>
""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="chat-bubble-ai">🤖 {chat["content"]}</div>
""", unsafe_allow_html=True)

# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Ask something...")

if user_input:
    # USER MESSAGE
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    st.markdown(f"""
<div class="chat-bubble-user">👤 {user_input}</div>
""", unsafe_allow_html=True)

    # AI RESPONSE
    with st.spinner("🤖 Thinking..."):
        response = run_agent(user_input, st.session_state.thread_id)

    # Typing animation
    placeholder = st.empty()
    typed_text = ""

    for char in response:
        typed_text += char
        placeholder.markdown(f"""
<div class="chat-bubble-ai">🤖 {typed_text}</div>
""", unsafe_allow_html=True)
        time.sleep(0.003)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })