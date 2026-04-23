"""
rag_chain.py (STABLE - NO langchain-groq dependency)
"""

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from config import GROQ_API_KEY, GROQ_MODEL
from vectorstore import get_retriever


# ─────────────────────────────
# LLM (USING GROQ VIA OPENAI-COMPATIBLE API)
# ─────────────────────────────
def _build_llm():
    return ChatOpenAI(
        openai_api_key=GROQ_API_KEY,
        openai_api_base="https://api.groq.com/openai/v1",
        model=GROQ_MODEL,
        temperature=0.2,
        max_tokens=2048,
    )


# ─────────────────────────────
# Memory
# ─────────────────────────────
def _build_memory():
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )


# ─────────────────────────────
# Prompt
# ─────────────────────────────
QA_PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template="""
You are a Tamil Nadu college admissions assistant.

Context:
{context}

Chat History:
{chat_history}

Question:
{question}

Answer clearly with bullet points if needed.
"""
)


# ─────────────────────────────
# RAG CHAIN
# ─────────────────────────────
def build_rag_chain(vectorstore):
    llm = _build_llm()
    memory = _build_memory()
    retriever = get_retriever(vectorstore)

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
    )


# ─────────────────────────────
# Helper
# ─────────────────────────────
def ask(chain, question: str):
    return chain.invoke({"question": question})