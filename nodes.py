import os
import warnings
warnings.filterwarnings("ignore")

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from tools import jd_analyzer
from groq import Groq

# 🔥 PUT YOUR GROQ API KEY HERE
client = Groq(api_key="your_api_key_here")

# Load vector DB
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="vectordb", embedding_function=embedding)


# ---------------- MEMORY ----------------
# ---------------- MEMORY ----------------
def memory_node(state):
    text = state["user_input"]
    lower = text.lower()

    # -------- NAME --------
    if "my name is" in lower:
        name_part = lower.split("my name is")[-1].strip()
        name = name_part.split()[0]
        state["name"] = name.capitalize()

    # -------- SKILLS --------
    if "i know" in lower:
        skills_part = lower.split("i know")[-1]

        # clean separators
        skills_part = skills_part.replace("and", ",")
        skills = [s.strip() for s in skills_part.split(",") if s.strip()]

        state["skills"] = skills

    # -------- TARGET ROLE --------
    if "i want" in lower or "target role" in lower:
        if "i want" in lower:
            role = lower.split("i want")[-1].strip()
        else:
            role = lower.split("target role")[-1].strip()

        state["target_role"] = role

    return state


# ---------------- ROUTER ----------------
def router_node(state):
    q = state["user_input"].lower()

    # -------- RESUME --------
    if "resume" in q:
        state["route"] = "resume"

    # -------- TOOL (JD ANALYSIS) --------
    elif any(word in q for word in [
        "jd", "job description", "requirements",
        "should i apply", "match", "eligibility",
        "am i fit", "am i suitable"
    ]):
        state["route"] = "tool"

    # -------- RAG (PLACEMENT KNOWLEDGE) --------
    elif any(word in q for word in [
        "dsa", "roadmap", "interview", "hr",
        "aptitude", "placement", "strategy",
        "preparation", "tips", "how to prepare"
    ]):
        state["route"] = "rag"

    # -------- DEFAULT --------
    else:
        state["route"] = "rag"

    return state
# ---------------- RETRIEVAL ----------------
def retrieval_node(state):
    query = state["user_input"]

    try:
        docs = db.similarity_search(query, k=3)

        if not docs:
            state["retrieved_docs"] = []
        else:
            state["retrieved_docs"] = [d.page_content for d in docs]

    except:
        state["retrieved_docs"] = []

    return state

# ---------------- TOOL ----------------
def tool_node(state):
    user_input = state["user_input"]
    user_skills = state.get("skills", [])

    try:
        result = jd_analyzer(user_input, user_skills)

        # 🔥 ensure structured + safe output
        state["tool_output"] = {
            "match_percentage": result.get("match_percentage", 0),
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "recommendation": result.get("recommendation", "Not suitable")
        }

    except Exception as e:
        state["tool_output"] = {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendation": "Error",
            "error": str(e)
        }

    return state
# ---------------- ANSWER (GROQ) ----------------
def answer_node(state):
    route = state.get("route")

    name = state.get("name")
    skills = state.get("skills")
    role = state.get("target_role")

    memory_context = f"""
User Profile:
Name: {name}
Skills: {skills}
Target Role: {role}
"""

    query = state["user_input"].lower()

    import re

    # -------- MEMORY STORE (FIXED) --------
    match = re.search(r"\b(my name is|i am)\b\s+([a-zA-Z]+)", query)

    if match:
        extracted_name = match.group(2).capitalize()
        state["name"] = extracted_name
        state["response"] = f"Nice to meet you, {extracted_name}."
        return state

    # -------- MEMORY RECALL --------
    if "name" in query and any(x in query for x in ["what", "remember", "my", "tell"]):
        if name:
            state["response"] = f"Your name is {name}."
        else:
            state["response"] = "I don't know your name yet."
        return state

    # -------- GENERAL ASSISTANT QUERIES --------
    general_queries = [
        "who are you", "what are you", "what is your work",
        "what can you do", "your purpose"
    ]

    if any(g in query for g in general_queries):
        state["response"] = (
            "I am an AI Placement Assistant. I help with:\n"
            "- DSA preparation\n"
            "- Resume building\n"
            "- Job description analysis\n"
            "- Interview preparation\n"
            "- Placement strategy"
        )
        return state

    # -------- TOOL --------
    if route == "tool":
        result = state.get("tool_output", {})

        matched = result.get("matched_skills") or []
        missing = result.get("missing_skills") or []

        state["response"] = f"""
📊 Job Match Analysis

✔ Match: {result.get("match_percentage", 0)}%

✔ Matched Skills:
{', '.join(map(str, matched)) if matched else 'None'}

❌ Missing Skills:
{', '.join(map(str, missing)) if missing else 'None'}

📌 Recommendation: {result.get("recommendation", "Not available")}
"""
        return state

    # -------- RESUME --------
    if route == "resume":
        prompt = f"""
Create a professional fresher resume.

Use:
{memory_context}

Make sections:
- Summary
- Skills
- Projects
- Education
"""
    else:
        # -------- DOMAIN FILTER (SOFT) --------
        placement_keywords = [
            "dsa", "interview", "hr", "resume", "placement",
            "job", "skills", "roadmap", "aptitude", "backend"
        ]

        if not any(word in query for word in placement_keywords):
            docs = []
            context = ""
        else:
            docs = state.get("retrieved_docs", [])
            context = "\n\n".join(docs) if docs else ""

        # -------- RAG --------
        prompt = f"""
You are an intelligent placement assistant.

Give answers in:
- Clear heading
- Bullet points
- Short and practical

Rules:
- Use context if available
- If context is weak, still answer intelligently within placement domain
- Avoid long paragraphs
- Avoid repetition

{memory_context}

Context:
{context}

Question:
{state['user_input']}
"""

    # -------- LLM CALL --------
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        state["response"] = res.choices[0].message.content

    except Exception:
        state["response"] = "System error"

    return state
# ---------------- EVAL ----------------
def eval_node(state):
    response = state.get("response", "")
    docs = state.get("retrieved_docs", [])

    # -------- SIMPLE BUT PRACTICAL --------
    if len(response.strip()) < 30:
        score = 0.2
    elif "I don't know" in response:
        score = 0.3
    else:
        score = 0.9   # assume good answer

    state["score"] = score

    print(f"Evaluation Score: {state['score']}")

    # -------- RETRY --------
    if score < 0.4 and state.get("retries", 0) < 2:
        print("RETRYING...")
        state["retries"] += 1
        state["route"] = "rag"
    else:
        print("PASS")

    return state
# ---------------- SAVE ----------------
def save_node(state):
    return state
