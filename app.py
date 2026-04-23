"""
app.py
─────────────────────────────────────────────────────────────────
Tamil Nadu College Admissions AI — Streamlit entry point.

This file is intentionally thin: it only handles page config,
session-state initialisation, layout, and tab routing.
All heavy logic lives in the modules it imports.

Architecture
────────────
  .env  ──► config.py  ──► pipeline.py (cached)
                               ├─ data_loader.py
                               ├─ vectorstore.py
                               └─ rag_chain.py
                                       └─ prompts.py
  pages/
    sidebar.py      ← sidebar widgets
    chat_tab.py     ← AI chat (uses agent.py + rag_chain.ask)
    colleges_tab.py ← Browse colleges
    checklist_tab.py← Step-by-step checklist

Run:  streamlit run app.py
─────────────────────────────────────────────────────────────────
"""

import streamlit as st

# ── Page config — MUST be the very first Streamlit call ──────────
st.set_page_config(
    page_title="TN Admissions AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Project-level imports (after page config) ────────────────────
from pipeline import initialize          # builds RAG chain (cached)
from styles import inject_styles         # injects CSS
from pages.sidebar import render as render_sidebar
from pages.chat_tab import render as render_chat
from pages.colleges_tab import render as render_colleges
from pages.checklist_tab import render as render_checklist


# ── Session state defaults ────────────────────────────────────────
def _init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


# ── Main ──────────────────────────────────────────────────────────
def main() -> None:
    inject_styles()
    _init_session()

    # ── Build the RAG pipeline (runs once, then cached) ───────
    try:
        chain, data = initialize()
    except EnvironmentError as exc:
        # config.py raises EnvironmentError when .env key is missing
        st.error(str(exc))
        st.stop()

    # ── Sidebar ───────────────────────────────────────────────
    with st.sidebar:
        render_sidebar(data)

    # ── Page header ───────────────────────────────────────────
    st.markdown(
        """
        <div class="main-header">
            <h1 class="header-title">🎓 Tamil Nadu College Admissions AI</h1>
            <p class="header-subtitle">
                Your intelligent guide for eligibility · required documents ·
                deadlines · step-by-step checklists &nbsp;|&nbsp;
                Powered by <strong style="color:#f97316;">Groq LLaMA 3</strong>
                + <strong style="color:#3b82f6;">LangChain RAG</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tabs ──────────────────────────────────────────────────
    tab_chat, tab_colleges, tab_checklist = st.tabs(
        ["💬 AI Chat", "🏛 Browse Colleges", "📋 Checklist"]
    )

    with tab_chat:
        render_chat(chain)

    with tab_colleges:
        render_colleges(data)

    with tab_checklist:
        render_checklist(data)


if __name__ == "__main__":
    main()
