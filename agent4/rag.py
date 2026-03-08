"""
rag.py — Retrieval-Augmented Generation engine for tool man pages.

Uses ChromaDB (local, persistent) + sentence-transformers for embedding.
Call `ingest_manpages.py` once to populate the DB, then use `query_docs` at runtime.
"""

import os
from typing import Optional, List
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import ollama

# --- Config ---
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "manpages"
EMBED_MODEL = "nomic-embed-text:latest"   # any ollama embedding model
TOP_K = 5                           # number of chunks to retrieve

# --- Custom Ollama embedding function for ChromaDB ---
class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model: str = EMBED_MODEL):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            response = ollama.embeddings(model=self.model, prompt=text)
            embeddings.append(response["embedding"])
        return embeddings


# --- Singleton client / collection ---
_client: Optional[chromadb.PersistentClient] = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        ef = OllamaEmbeddingFunction(model=EMBED_MODEL)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def ingest_document(doc_id: str, text: str, metadata: Optional[dict] = None):
    """
    Chunk and upsert a document (e.g. a man page) into the vector store.

    Args:
        doc_id:   Unique identifier, e.g. "nmap" or "volatility3".
        text:     Full text of the man page / documentation.
        metadata: Optional dict of extra fields (tool name, source, etc.).
    """
    collection = _get_collection()
    chunks = _chunk_text(text, chunk_size=400, overlap=50)
    ids       = [f"{doc_id}::{i}" for i in range(len(chunks))]
    metadatas = [{**(metadata or {}), "doc_id": doc_id, "chunk": i} for i in range(len(chunks))]

    # Upsert so re-running ingest is idempotent
    collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
    print(f"  ✓ Ingested '{doc_id}' → {len(chunks)} chunks")


def query_docs(query: str, top_k: int = TOP_K, tool_filter: Optional[str] = None) -> str:
    """
    Retrieve the most relevant documentation chunks for a query.

    Args:
        query:       Natural-language question or user request.
        top_k:       How many chunks to return.
        tool_filter: If set, restrict results to a specific tool doc_id.

    Returns:
        A single string of concatenated relevant chunks, ready to inject into a prompt.
    """
    collection = _get_collection()
    if collection.count() == 0:
        return ""   # nothing ingested yet — degrade gracefully

    where = {"doc_id": tool_filter} if tool_filter else None
    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
        where=where,
        include=["documents", "metadatas"],
    )

    chunks = results["documents"][0]        # list of strings
    metas  = results["metadatas"][0]        # list of dicts

    if not chunks:
        return ""

    parts = []
    for chunk, meta in zip(chunks, metas):
        tool = meta.get("doc_id", "unknown")
        parts.append(f"[{tool} docs]\n{chunk}")

    return "\n\n---\n\n".join(parts)


# --- Internal helpers ---

def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    """Split text into overlapping word-level chunks."""
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks