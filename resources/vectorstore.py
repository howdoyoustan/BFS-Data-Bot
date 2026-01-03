from vectorstore.chrome_store import get_chroma_vectorstore

def get_vectorstore():
    """
    Returns the singleton Chroma vector store.
    Safe to call from multiple nodes.
    """
    return get_chroma_vectorstore()
