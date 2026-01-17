from langgraph.graph import StateGraph, START, END
from graph.state import GraphState
from graph.nodes.retrieve import retrieve_node
from graph.nodes.relevance import relevance_grader_node
from graph.nodes.generate import generate_node
from graph.nodes.hallucination import hallucination_grader_node
from graph.nodes.retry_generate import retry_generate_node
from graph.nodes.improve_kb import improve_kb
from graph.routers import decide_after_relevance, decide_final_step

workflow = StateGraph(GraphState)

# ------------------
# Add nodes
# ------------------
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("relevance_grader", relevance_grader_node)
workflow.add_node("generate", generate_node)
workflow.add_node("hallucination_grader", hallucination_grader_node)
workflow.add_node("retry_generate", retry_generate_node)
workflow.add_node("improve_kb", improve_kb)

# ------------------
# Entry
# ------------------
workflow.add_edge(START, "retrieve")

# ------------------
# Retrieval → relevance
# ------------------
workflow.add_edge("retrieve", "relevance_grader")

workflow.add_conditional_edges(
    "relevance_grader",
    decide_after_relevance,
    {
        "generate": "generate",
        "improve_kb": "improve_kb",
    },
)

# ------------------
# Improve KB → retrieve again
# ------------------
workflow.add_edge("improve_kb", "retrieve")

# ------------------
# Generate → hallucination check
# ------------------
workflow.add_edge("generate", "hallucination_grader")
workflow.add_edge("retry_generate", "hallucination_grader")

# ------------------
# Final decision router
# ------------------
workflow.add_conditional_edges(
    "hallucination_grader",
    decide_final_step,
    {
        "retry_generate": "retry_generate",
        "improve_kb": "improve_kb",
        "finalize": END,
    },
)

# ------------------
# Compile graph
# ------------------
app = workflow.compile()
