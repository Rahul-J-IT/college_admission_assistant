"""
vectorstore.py
─────────────────────────────────────────────────────────────────
Responsibility:
  1. Split LangChain Documents into fixed-size chunks
  2. Embed each chunk with a local HuggingFace sentence-transformer
  3. Store embeddings in an in-memory FAISS index
  4. Expose a LangChain Retriever for use by the RAG chain

No API key is required — embeddings run 100% locally on CPU.

Public API
----------
build_vectorstore(docs)  -> FAISS
get_retriever(vs)        -> VectorStoreRetriever
─────────────────────────────────────────────────────────────────
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import EMBEDDING_MODEL, RETRIEVER_TOP_K


# ── Chunk settings ────────────────────────────────────────────────
_CHUNK_SIZE    = 800   # characters per chunk
_CHUNK_OVERLAP = 100   # overlap between adjacent chunks


# ── Private helpers ───────────────────────────────────────────────
def _make_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )


def _make_embeddings() -> HuggingFaceEmbeddings:
    """
    Load the sentence-transformer model locally.
    First run downloads the model (~90 MB); subsequent runs use cache.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


# ── Public API ────────────────────────────────────────────────────
def build_vectorstore(docs: List[Document]) -> FAISS:
    """
    Chunk → embed → index.
    Returns a FAISS vector store loaded with all college chunks.
    """
    chunks     = _make_splitter().split_documents(docs)
    embeddings = _make_embeddings()
    return FAISS.from_documents(chunks, embeddings)


def get_retriever(vectorstore: FAISS):
    """
    Wrap the FAISS store in a LangChain retriever.
    Returns top-k most similar chunks for any query.
    """
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_TOP_K},
    )
