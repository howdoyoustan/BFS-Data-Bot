"""
Vector store package.

This package owns:
- Vector database initialization
- Embedding configuration
- Safe accessors for vector stores

Rules:
- No writes happen at import time
- No LLM logic lives here
- Only improve_kb is allowed to write to the vector DB
"""

from .chrome_store import get_chroma_vectorstore

__all__ = [
    "get_chroma_vectorstore",
]
