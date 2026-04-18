from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import *

def build_graph():
    g = StateGraph(AgentState)

    # Nodes
    g.add_node("memory", memory_node)
    g.add_node("router", router_node)
    g.add_node("retrieval", retrieval_node)
    g.add_node("tool", tool_node)
    g.add_node("answer", answer_node)
    g.add_node("eval", eval_node)
    g.add_node("save", save_node)

    # Entry
    g.set_entry_point("memory")

    # Flow
    g.add_edge("memory", "router")

    g.add_conditional_edges(
        "router",
        lambda s: s["route"],
        {
            "rag": "retrieval",
            "tool": "tool",
            "resume": "answer",
            "default": "answer"
        }
    )

    g.add_edge("retrieval", "answer")
    g.add_edge("tool", "answer")
    g.add_edge("answer", "eval")

    # 🔥 FIXED: retry logic added
    g.add_conditional_edges(
        "eval",
        lambda s: "retry" if s["score"] < 0.4 and s["retries"] < 2 else "done",
        {
            "retry": "router",
            "done": "save"
        }
    )

    g.add_edge("save", END)

    # Memory
    memory = MemorySaver()

    return g.compile(checkpointer=memory)