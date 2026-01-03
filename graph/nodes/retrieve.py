from langchain_openai import ChatOpenAI
from vectorstore.chrome_store import get_chroma_vectorstore
from dotenv import load_dotenv

load_dotenv(override=True)

llm = ChatOpenAI(model="gpt-4o", temperature=0)
vectorstore = get_chroma_vectorstore()

def retrieve_node(state):
    print("---Retrieving from BFS Vector Store---")
    
    retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 10,
        "score_threshold": 0.60
    }
    )

    #Assuming we have a retriever object
    documents = retriever.invoke(state["question"])

    #Return documents and update the state
    return {"documents": documents, "steps": ["retrieve_documents"]}