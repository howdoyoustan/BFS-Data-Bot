from resources.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# -------------------------
# Initialize shared LLM
# -------------------------
llm = get_llm()


HIGH_CONFIDENCE = 0.78  # auto-accept
LOW_CONFIDENCE  = 0.60   # auto-reject


def embedding_relevance_filter(docs, threshold_high=HIGH_CONFIDENCE, threshold_low=LOW_CONFIDENCE):
    accepted = []
    borderline = []

    for doc in docs:
        score = doc.metadata.get("similarity", 0)

        if score >= threshold_high:
            accepted.append(doc)
        elif score >= threshold_low:
            borderline.append(doc)
        # else: reject silently

    return accepted, borderline


relevance_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a document relevance grader for Banking & Financial Services
Apache Spark incident analysis.

STRICTNESS RUBRIC:
- Mark YES if the document contains:
  • logs, configs, job IDs, API names, or error codes mentioned in the question
  • partial evidence related to the failure, even if no solution is present
- Mark NO only if the document is clearly about a different job, system,
  technology, or an unrelated error.

IMPORTANT:
- Be liberal: prefer YES if unsure
- Be firm: reject clearly unrelated documents
Return ONLY 'yes' or 'no'."""),
    ("human",
     "Question:\n{question}\n\nDocument:\n{context}")
])


class GradeDocuments(BaseModel):
    binary_score: str = Field(description="Relevant to question, 'yes' or 'no'")


# ✅ Structured-output LLM (instance method)
structured_llm_relevance = llm.with_structured_output(GradeDocuments)


def relevance_grader_node(state):
    print("--- HYBRID RELEVANCE CHECK ---")

    question = state["question"]
    docs = state["documents"]

    accepted, borderline = embedding_relevance_filter(docs)

    # LLM fallback only for borderline docs
    for doc in borderline:
        result = structured_llm_relevance.invoke(
            relevance_prompt.format_messages(
                question=question,
                context=doc.page_content
            )
        )

        if result.binary_score.lower() == "yes":
            accepted.append(doc)

    return {
        "documents": accepted,
        "is_relevant": "yes" if accepted else "no",
        "steps": [
            f"embedding_accept:{len(accepted)}",
            f"llm_reviewed:{len(borderline)}"
        ]
    }
