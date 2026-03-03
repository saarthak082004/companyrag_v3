import streamlit as st
import os
import time
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from groq import Groq

from database import (
    signup_user,
    login_user,
    create_new_chat,
    get_user_chats,
    get_chat_messages,
    save_message,
    update_chat_title,
    hide_chat
)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="IntraRAG – Intelligent Enterprise Knowledge Assistant",
    page_icon="🧠",
    layout="wide"
)

# ================= PROFESSIONAL CSS =================
st.markdown("""
<style>
.main { background-color: #f4f6fb; }
section[data-testid="stSidebar"] { background-color: #111827; }
section[data-testid="stSidebar"] * { color: white; }
.stChatMessage { border-radius: 12px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= LOAD ENV =================
load_dotenv()
pinecone_key = os.getenv("PINECONE_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
synise_index_name = os.getenv("SYNISE_INDEX_NAME")
public_counsel_index_name = os.getenv("PUBLIC_COUNSEL_INDEX_NAME")

# ================= LOAD SYSTEM PROMPT =================
def load_system_prompt():
    try:
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are IntraRAG. Answer only using company context."

system_prompt = load_system_prompt()

# ================= COMPANY DETECTION =================
def detect_company(email):
    email = email.lower().strip()
    if email.endswith("@synise.com"):
        return "Synise"
    elif email.endswith("@publiccounsel.org"):
        return "Public Counsel"
    return None

# ================= LOAD MODELS =================
@st.cache_resource
def load_models():
    embed_model = SentenceTransformer("all-mpnet-base-v2")
    groq_client = Groq(api_key=groq_key)
    return embed_model, groq_client

embed_model, groq_client = load_models()

# ================= INDEX LOADER =================
def get_company_index(company):
    pc = Pinecone(api_key=pinecone_key)
    if company == "Synise":
        return pc.Index(synise_index_name)
    elif company == "Public Counsel":
        return pc.Index(public_counsel_index_name)
    return None

# ================= SESSION INIT =================
for key, default in {
    "logged_in": False,
    "user_email": "",
    "user_name": "",
    "company": "",
    "current_chat": None,
    "messages": [],
    "model": "llama-3.3-70b-versatile"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ================= AUTH =================
if not st.session_state.logged_in:

    st.markdown("<h1 style='text-align:center;'>🧠 IntraRAG</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:gray;'>Intelligent Enterprise Knowledge Assistant</h4>", unsafe_allow_html=True)

    col = st.columns([1,2,1])[1]

    with col:
        tab1, tab2 = st.tabs(["Login", "Signup"])

        # LOGIN
        with tab1:
            email_l = st.text_input("Work Email", key="login_email")
            password_l = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", use_container_width=True):
                user = login_user(email_l, password_l)
                if user:
                    detected_company = detect_company(email_l)
                    if detected_company and detected_company == user[1]:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_l
                        st.session_state.user_name = user[0]
                        st.session_state.company = user[1]
                        st.rerun()
                    else:
                        st.error("Invalid company email.")
                else:
                    st.error("Invalid email or password.")

        # SIGNUP
        with tab2:
            name_s = st.text_input("Full Name", key="signup_name")
            email_s = st.text_input("Work Email", key="signup_email")
            password_s = st.text_input("Password", type="password", key="signup_password")

            if st.button("Create Account", use_container_width=True):
                detected_company = detect_company(email_s)

                if not detected_company:
                    st.error("Use official company email.")
                else:
                    result = signup_user(name_s, email_s, password_s, detected_company)

                    if result == "success":
                        st.success("Account created successfully!")
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_s
                        st.session_state.user_name = name_s
                        st.session_state.company = detected_company
                        st.rerun()
                    else:
                        st.error(result)

    st.stop()

# ================= SIDEBAR =================
st.sidebar.markdown("## 🧠 IntraRAG")
st.sidebar.markdown(f"👤 {st.session_state.user_name}")
st.sidebar.markdown(f"🏢 {st.session_state.company}")
st.sidebar.divider()

st.sidebar.selectbox(
    "Model",
    ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"],
    key="model"
)

if st.sidebar.button("➕ New Chat"):
    st.session_state.current_chat = None
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("### 💬 Chats")

chats = get_user_chats(st.session_state.user_email)

for chat_id, title in chats[:15]:
    display_title = title if title else "Untitled Chat"

    col1, col2 = st.sidebar.columns([0.85, 0.15])

    if col1.button(display_title, key=f"chat_{chat_id}"):

        st.session_state.current_chat = chat_id
        loaded_messages = get_chat_messages(chat_id)

        st.session_state.messages = []
        for m in loaded_messages:
            st.session_state.messages.append({
                "role": m.get("role"),
                "content": m.get("content"),
                "model": m.get("model"),
                "response_time": m.get("response_time"),
            })

        st.rerun()

    if col2.button("🗑", key=f"hide_{chat_id}"):
        hide_chat(chat_id)
        st.rerun()

if st.sidebar.button("Logout"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ================= CHAT AREA =================
st.markdown(f"### Welcome, {st.session_state.user_name}")
st.caption("Secure internal enterprise knowledge access.")

# -------- DISPLAY OLD MESSAGES PROPERLY --------
for msg in st.session_state.messages:

    role = msg.get("role")
    content = msg.get("content")
    model = msg.get("model")
    response_time = msg.get("response_time")

    with st.chat_message(role):
        st.markdown(content)

        if role == "assistant":
            meta_parts = []

            if response_time is not None:
                meta_parts.append(f"⏱ {response_time} sec")

            if model:
                meta_parts.append(f"🤖 {model}")

            if meta_parts:
                st.caption(" | ".join(meta_parts))

# ================= CHAT INPUT =================
query = st.chat_input("Ask about internal company knowledge...")

if query:

    new_chat = False

    if st.session_state.current_chat is None:
        st.session_state.current_chat = create_new_chat(
            st.session_state.user_email,
            st.session_state.user_name,
            st.session_state.company
        )
        new_chat = True

    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    save_message(
        st.session_state.current_chat,
        st.session_state.user_email,
        "user",
        query
    )

    if new_chat:
        update_chat_title(st.session_state.current_chat, query[:40])

    with st.chat_message("assistant"):
        placeholder = st.empty()
        start_time = time.time()

        query_vector = embed_model.encode(query).tolist()
        index = get_company_index(st.session_state.company)

        print("Retrieval happening: querying index")
        results = index.query(
            vector=query_vector,
            top_k=6,
            
            include_metadata=True
        )

        context_text = "\n\n".join(
            match["metadata"].get("text", "")
            for match in results.get("matches", [])
        )

        response = groq_client.chat.completions.create(
            model=st.session_state.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion:\n{query}"}
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()

        full = ""
        for char in answer:
            full += char
            placeholder.markdown(full)
            time.sleep(0.001)

        total_time = round(time.time() - start_time, 2)
        st.caption(f"⏱ {total_time} sec | 🤖 {st.session_state.model}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "model": st.session_state.model,
        "response_time": total_time
    })

    save_message(
        st.session_state.current_chat,
        st.session_state.user_email,
        "assistant",
        answer,
        st.session_state.model,
        total_time
    )