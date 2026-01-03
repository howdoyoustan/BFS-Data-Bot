import hashlib
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ----------------------------
# Config
# ----------------------------
ALLOWED_SOURCES = {
    "web_search",
    "internal_logs",
    "official_docs",
    "runbooks",
}

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
)

# ----------------------------
# Helpers
# ----------------------------
def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ----------------------------
# Main write function
# ----------------------------
def write_to_vector_db(docs, vectorstore) -> int:
    """
    Writes NEW, VALID documents to the vector DB.
    Returns number of newly stored chunks.
    """

    stored_chunks = 0

    for doc in docs:
        # 1. Validate source
        source = doc.metadata.get("source")
        if source not in ALLOWED_SOURCES:
            continue

        content = doc.page_content.strip()
        if not content:
            continue

        # 2. Normalize + stable document ID
        doc_id = _hash_text(content)

        base_metadata = {
            **doc.metadata,
            "doc_id": doc_id,
        }

        # 3. Chunk
        chunks = text_splitter.split_text(content)

        documents_to_add = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"

            documents_to_add.append(
                Document(
                    page_content=chunk,
                    metadata={
                        **base_metadata,
                        "chunk_id": chunk_id,
                    },
                )
            )

        if not documents_to_add:
            continue

        # 4. Deduplication (Chroma handles ID conflicts safely)
        try:
            vectorstore.add_documents(
                documents_to_add,
                ids=[d.metadata["chunk_id"] for d in documents_to_add],
            )
            stored_chunks += len(documents_to_add)
        except Exception:
            # Duplicate IDs or other safe failures
            continue

    return stored_chunks
