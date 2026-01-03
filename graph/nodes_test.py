# graph/nodes.py

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from vectorstore import get_chroma_vectorstore
from utils.vector_write_pipeline import write_to_vector_db
from utils.query_rewrite import question_rewriter
from utils.search import web_search_tool


# ============================================================
# LLM SETUP
# ============================================================

llm = ChatOpenAI(model="gpt-4o", temperature=0)

vectorstore = get_chroma_vectorstore()


# ============================================================
# STRUCTURED OUTPUT MODELS
# ============================================================

class GradeDocuments(BaseModel):
    binary_score: str = Field(description="Relevant: 'yes' or 'no'")


class GradeHallucinations(BaseModel):
    binary_score: str = Field(description="Grounded: 'yes' or 'no'")


# ============================================================
# RETRIEVE NODE
# ============================================================

def retrieve_node(state):
    print("--- RETRIEVING DOCUMENTS ---")

    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 10,
            "score_threshold": 0.60,
        },
    )

    docs = retriever.get_relevant_documents(state["question"])

    return {
        "documents": docs,
        "steps": ["retrieve"],
    }


# ============================================================
# RELEVANCE GRADER NODE (HYBRID)
# ============================================================

relevance_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a document relevance grader for BFS Spark incident analysis.

RULES:
- Mark YES if the document contains logs, configs, job IDs,
  API names, or error codes related to the question.
- Mark NO only if it is clearly about a different system or job.
- Be liberal but firm.

Return ONLY 'yes' or 'no'."""),
    ("human", "Question:\n{question}\n\nDocument:\n{context}")
])

structured_relevance_llm = llm.with_structured_output(GradeDocuments)


def relevance_grader_node(state):
    print("--- CHECKING RELEVANCE ---")

    accepted = []

    for doc in state["documents"]:
        result = structured_relevance_llm.invoke(
            relevance_prompt.format_messages(
                question=state["question"],
                context=doc.page_content,
            )
        )

        if result.binary_score.lower() == "yes":
            accepted.append(doc)

    return {
        "documents": accepted,
        "is_relevant": "yes" if accepted else "no",
        "steps": ["relevance_grader"],
    }


# ============================================================
# GENERATE NODE
# ============================================================

SYSTEM_PROMPT = """
You are a Senior Data Engineer specializing in BFS Spark pipelines.

RULES:
- Use ONLY the provided context.
- Quote logs when relevant.
- Do NOT infer configurations or causes.
- If context is insufficient, respond EXACTLY with:
  "I don't know - The current knowledge base is insufficient to answer this."
"""


def generate_node(state):
    print("--- GENERATING ANSWER ---")

    if not state["documents"]:
        return {
            "generation": "I don't know - The current knowledge base is insufficient to answer this.",
            "steps": ["generate_no_context"],
        }

    context = "\n\n".join(
        f"[DOC {i}]\n{doc.page_content}"
        for i, doc in enumerate(state["documents"])
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": state["question"],
    })

    return {
        "generation": answer,
        "steps": ["generate"],
    }


# ============================================================
# HALLUCINATION GRADER NODE
# ============================================================

hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a hallucination detector.

Mark NO if ANY claim is not explicitly supported by the documents.
Mark YES only if every statement is grounded.

Return ONLY 'yes' or 'no'."""),
    ("human", "Documents:\n{documents}\n\nAnswer:\n{generation}")
])

structured_hallucination_llm = llm.with_structured_output(GradeHallucinations)


def hallucination_grader_node(state):
    print("--- CHECKING HALLUCINATIONS ---")

    docs = "\n\n".join(
        f"[DOC {i}]\n{doc.page_content}"
        for i, doc in enumerate(state["documents"])
    )

    result = structured_hallucination_llm.invoke(
        hallucination_prompt.format_messages(
            documents=docs,
            generation=state["generation"],
        )
    )

    return {
        "is_grounded": result.binary_score.lower(),
        "steps": ["hallucination_grader"],
    }


# ============================================================
# RETRY GENERATE NODE (STRICT)
# ============================================================

RETRY_SYSTEM_PROMPT = """
You are retrying generation after a hallucination.

RULES:
- Remove unsupported claims.
- Do NOT infer.
- Prefer quoting logs.
- If unsure, respond EXACTLY with:
  "I don't know - The current knowledge base is insufficient to answer this."
"""


def retry_generate_node(state):
    print("--- RETRY GENERATION ---")

    context = "\n\n".join(
        f"[DOC {i}]\n{doc.page_content}"
        for i, doc in enumerate(state["documents"])
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", RETRY_SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": state["question"],
    })

    return {
        "generation": answer,
        "retry_generation_count": state.get("retry_generation_count", 0) + 1,
        "steps": ["retry_generate"],
    }


# ============================================================
# IMPROVE KB NODE
# ============================================================

def improve_kb(state):
    print("--- IMPROVING KNOWLEDGE BASE ---")

    kb_retry_count = state.get("kb_retry_count", 0)

    rewritten_query = question_rewriter.invoke({
        "question": state["question"]
    })

    new_docs = web_search_tool.invoke({
        "query": rewritten_query
    }) or []

    stored_chunks = write_to_vector_db(
        docs=new_docs,
        vectorstore=vectorstore,
    )

    kb_enriched = stored_chunks > 0

    return {
        "documents": new_docs,
        "kb_retry_count": kb_retry_count + 1,
        "kb_enriched": kb_enriched,
        "steps": [
            f"improve_kb_attempt_{kb_retry_count + 1}",
            f"stored_chunks:{stored_chunks}",
        ],
    }
