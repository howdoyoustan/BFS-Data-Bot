# vectorstore/chroma_store.py

import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# --------------------
# Configuration
# --------------------
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    "./chroma_db"
)

EMBEDDING_MODEL = "text-embedding-3-large"

# --------------------
# Embeddings
# --------------------
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# --------------------
# Vector Store Factory
# --------------------
def get_chroma_vectorstore(collection_name="bfs_rag"):
    """
    Returns a persistent Chroma vector store.
    Safe to call multiple times.
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
