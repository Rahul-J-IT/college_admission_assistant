"""
pipeline.py
─────────────────────────────────────────────────────────────────
Top-level initialisation — wires every backend module together.

Call initialize() once at Streamlit startup.
Streamlit's @st.cache_resource ensures the heavy work
(embedding model download + FAISS index build) runs only once,
even across page reruns.

Dependency order
----------------
  config
    └─ data_loader  →  build_documents()
    └─ vectorstore  →  build_vectorstore(docs)
    └─ rag_chain    →  build_rag_chain(vectorstore)
         ↑
       agent (used per-query in pages/chat_tab.py, not here)

Returns
-------
chain : ConversationalRetrievalChain  — ready for ask()
data  : dict                          — raw JSON for Browse / Checklist tabs
─────────────────────────────────────────────────────────────────
"""

import streamlit as st

from data_loader import build_documents, load_raw_data
from rag_chain import build_rag_chain
from vectorstore import build_vectorstore


@st.cache_resource(show_spinner="⚙️  Building RAG engine — this runs only once…")
def initialize():
    """
    Full pipeline startup.

    Steps
    -----
    1. Load JSON dataset                 (data_loader.load_raw_data)
    2. Convert to LangChain Documents    (data_loader.build_documents)
    3. Chunk + embed + index in FAISS    (vectorstore.build_vectorstore)
    4. Wire Groq LLM + retriever + chain (rag_chain.build_rag_chain)

    Cached by Streamlit — re-runs only when the Python process restarts.
    """
    docs        = build_documents()
    vectorstore = build_vectorstore(docs)
    chain       = build_rag_chain(vectorstore)
    data        = load_raw_data()
    return chain, data
