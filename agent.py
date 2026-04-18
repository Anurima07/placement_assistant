from graph import build_graph

app = build_graph()

def run_agent(user_input, thread_id):
    # 🔥 DO NOT include memory fields here
    state = {
        "user_input": user_input,
        "route": None,
        "retrieved_docs": [],
        "tool_output": {},
        "response": None,
        "score": 0,
        "retries": 0,
    }

    try:
        result = app.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}}
        )

        return result.get("response", "No response generated.")

    except Exception as e:
        return f"Error: {str(e)}"