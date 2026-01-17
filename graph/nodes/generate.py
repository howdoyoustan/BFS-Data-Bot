from prompts.sytem import GENERATOR_SYSTEM_PROMPT
from resources.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = get_llm()
def generate_node(state):
    print("--- GENERATING GROUNDED ANSWER ---")

    question = state["question"]
    documents = state["documents"]

    # If nothing survived relevance grading
    if not documents:
        return {
            "generation": "I don't know - The current knowledge base is insufficient to answer this.",
            "steps": ["generation_skipped_no_context"]
        }

    context = "\n\n".join(
        f"[DOC {i}]\n{doc.page_content}"
        for i, doc in enumerate(documents)
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", GENERATOR_SYSTEM_PROMPT),
        ("human",
         "Context:\n{context}\n\n"
         "Question:\n{question}\n\n"
         "Answer strictly using the context above.")
    ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return {
        "generation": response,
        "steps": ["generated_grounded_answer"]
    }
