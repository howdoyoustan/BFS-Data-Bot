from resources.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# -------------------------
# Initialize shared LLM
# -------------------------
llm = get_llm()


class GradeHallucinations(BaseModel):
    binary_score: str = Field(description="Grounded in facts, 'yes' or 'no'")


hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a hallucination detector for a Banking & Financial Services
Apache Spark incident analysis assistant.

RULES:
- Mark NO if the answer includes ANY claim not directly supported
  by the provided documents.
- Mark NO if the answer infers causes, configurations, or fixes
  not explicitly stated in the logs or docs.
- Mark YES only if EVERY statement can be traced to the documents.

Return ONLY 'yes' or 'no'."""),
    ("human",
     "Documents:\n{documents}\n\nAnswer:\n{generation}")
])


# ✅ This now works because llm is an INSTANCE
structured_llm_hallucination = llm.with_structured_output(GradeHallucinations)


def hallucination_grader_node(state):
    print("--- CHECKING FOR HALLUCINATIONS ---")

    documents = "\n\n".join(
        doc.page_content for doc in state["documents"]
    )

    result = structured_llm_hallucination.invoke(
        hallucination_prompt.format_messages(
            documents=documents,
            generation=state["generation"]
        )
    )

    return {
        "is_grounded": result.binary_score.lower(),
        "steps": ["hallucination_check"]
    }
