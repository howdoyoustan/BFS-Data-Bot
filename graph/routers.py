
def decide_after_relevance(state):
    if state["is_relevant"] == "no":
        return "improve_kb"
    return "generate"

def decide_final_step(state):
     # 1. Hallucination detected → retry generation (once)
    if state["is_grounded"] == "no":
        if state["retry_generation_count"] < 1:
            return "retry_generate"
        else:
            # Reasoning failed even after retry → try more data
            return "improve_kb"
    # 2. Safe but insufficient answer → improve KB (bounded)
    if "I don't know" in state["generation"]:
        if state["kb_retry_count"] < 3 and state.get("kb_enriched", True):
            return "improve_kb"
        else:
            # No more useful knowledge to add
            return "finalize"
    # 3. Grounded and useful answer
    return "finalize"

def decide_after_relevance(state):
    """
    If no relevant documents survived filtering,
    we must try to improve the knowledge base.
    """
    if state["is_relevant"] == "no":
        return "improve_kb"

    return "generate"
