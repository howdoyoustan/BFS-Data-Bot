from prompts.graders import RETRY_SYSTEM_PROMPT
from resources.llm import get_llm
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


llm = get_llm()
def retry_generate_node(state):
    print("--- RETRYING GENERATION (STRICT MODE) ---")

    question = state["question"]
    documents = state["documents"]

    context = "\n\n".join(
        f"[DOC {i}]\n{doc.page_content}"
        for i, doc in enumerate(documents)
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", RETRY_SYSTEM_PROMPT),
        ("human",
         "Context:\n{context}\n\n"
         "Question:\n{question}")
    ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return {
        "generation": response,
        "retry_generation_count": state.get("retry_generation_count", 0) + 1,
        "steps": ["retry_generation_strict"]
    }
