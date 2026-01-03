from prompts.graders import hallucination_prompt
from pydantic import BaseModel, Field
from resources import llm

class GradeHallucinations(BaseModel):
    binary_score: str = Field(description="Grounded in facts, 'yes' or 'no'")

structured_llm_hallucination = llm.with_structured_output(GradeHallucinations)

def hallucination_grader_node(state):
    print("--- CHECKING FOR HALLUCINATIONS ---")

    documents = "\n\n".join(
        f"[DOC {i}]\n{doc.page_content}"
        for i, doc in enumerate(state["documents"])
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

