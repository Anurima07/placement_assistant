from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    user_input: str
    
    name: Optional[str]
    skills: Optional[List[str]]
    branch: Optional[str]
    target_role: Optional[str]

    route: Optional[str]
    retrieved_docs: Optional[List[str]]
    tool_output: Optional[dict]

    response: Optional[str]

    score: Optional[float]
    retries: int

    thread_id: str