from langchain_openai import ChatOpenAI

def get_llm():
    """
    Factory for the main chat model.
    Centralized so behavior is consistent everywhere.
    """
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0
    )
