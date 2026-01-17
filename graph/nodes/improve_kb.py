from prompts.graders import RE_WRITE_PROMPT
from resources.llm import get_llm
from resources.vectorstore import get_vectorstore
from tools.web_search import web_search_tool
from tools.write_to_vector_db import write_to_vector_db
from langchain_core.output_parsers import StrOutputParser

# -------------------------
# Initialize shared resources
# -------------------------
llm = get_llm()
vectorstore = get_vectorstore()

# -------------------------
# Rewrite chain
# -------------------------
question_rewriter = RE_WRITE_PROMPT | llm | StrOutputParser()


def improve_kb(state):
    print("--- IMPROVING KNOWLEDGE BASE ---")

    question = state["question"]
    kb_retry_count = state.get("kb_retry_count", 0)

    # 1. Rewrite query for better recall
    improved_query = question_rewriter.invoke({
        "question": question
    })

    print(f"--- REWRITTEN QUERY ---\n{improved_query}")

    # 2. External search (logs, docs, APIs, etc.)
    try:
        new_docs = web_search.invoke({
            "query": improved_query
        })
    except Exception as e:
        print(f"--- WEB SEARCH FAILED: {e} ---")
        new_docs = []

    if not new_docs:
        return {
            "kb_retry_count": kb_retry_count + 1,
            "kb_enriched": False,
            "steps": [
                f"improve_kb_attempt_{kb_retry_count + 1}",
                "web_search_no_results"
            ],
        }
    # 3. Write ONLY valid, new content to vector DB
    stored_chunks = write_to_vector_db(
        docs=new_docs,
        vectorstore=vectorstore
    )

    # 4. Did we actually enrich the KB?
    kb_enriched = stored_chunks > 0

    return {
        # IMPORTANT: return only newly fetched docs
        # LangGraph will append via operator.add
        "documents": new_docs,
        "kb_retry_count": kb_retry_count + 1,
        "kb_enriched": kb_enriched,
        "steps": [
            f"improve_kb_attempt_{kb_retry_count + 1}",
            f"stored_chunks:{stored_chunks}"
        ]
    }
