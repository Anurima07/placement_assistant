from agent import run_agent

thread_id = "test_thread"

tests = [
    # -------- NORMAL --------
    "Give me DSA roadmap",
    "How to prepare for HR interview",
    "Resume tips for freshers",
    "Placement strategy",

    # -------- MEMORY --------
    "My name is Rima",
    "What is my name?",

    # -------- TOOL --------
    "JD: Python, SQL, ML required. I know Python. Should I apply?",

    # -------- EDGE --------
    "Tell me something random",
    "Explain quantum physics",

    # -------- CONTEXT --------
    "I know Java. Suggest backend roadmap."
]

for i, q in enumerate(tests):
    print("\n==============================")
    print(f"Test {i+1}: {q}")
    print("------------------------------")
    try:
        ans = run_agent(q, thread_id)
        print(ans)
    except Exception as e:
        print("ERROR:", e)