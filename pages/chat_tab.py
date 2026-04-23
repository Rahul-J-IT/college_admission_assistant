"""
pages/chat_tab.py
─────────────────────────────────────────────────────────────────
Renders the AI Chat tab:
  - Displays the full conversation history with intent badges
  - Shows expandable source-document references per AI reply
  - Handles the question input + Send button
  - Calls agent.process() for intent detection & query augmentation
  - Calls rag_chain.ask() to get the LLM answer
─────────────────────────────────────────────────────────────────
"""

import streamlit as st

from agent import INTENT_META, process
from rag_chain import ask


# ── Helpers ───────────────────────────────────────────────────────
def _intent_badge(intent: str) -> str:
    meta = INTENT_META.get(intent, INTENT_META["general"])
    return f'<span class="intent-badge {meta["badge"]}">{meta["label"]}</span>'


def _render_user_bubble(content: str) -> None:
    st.markdown(
        f'<div class="chat-user">'
        f'  <div class="chat-label label-user">👤 You</div>'
        f'  {content}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_ai_bubble(content: str, intent: str) -> None:
    badge = _intent_badge(intent)
    st.markdown(
        f'<div class="chat-ai">'
        f'  <div class="chat-label label-ai">🤖 AI Counselor &nbsp; {badge}</div>'
        f'  {content}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_sources(sources: list) -> None:
    if not sources:
        return
    with st.expander(f"📚 {len(sources)} source(s) used", expanded=False):
        for src in sources:
            m      = src.metadata
            label  = m.get("college_name", m.get("exam_key", m.get("doc_type", "Reference")))
            course = m.get("course_name", "")
            st.markdown(
                f'<div class="source-doc">📄 {label}'
                f'{" → " + course if course else ""}</div>',
                unsafe_allow_html=True,
            )


# ── Public renderer ───────────────────────────────────────────────
def render(chain) -> None:
    """Render the chat tab. `chain` is the ConversationalRetrievalChain from pipeline."""

    # ── Conversation history ──────────────────────────────────
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            _render_user_bubble(msg["content"])
        else:
            _render_ai_bubble(msg["content"], msg.get("intent", "general"))
            _render_sources(msg.get("sources", []))

    # ── Input row ─────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_input, col_btn = st.columns([5, 1])

    pending = st.session_state.pop("pending_question", "")

    with col_input:
        user_input = st.text_input(
            "question",
            value=pending,
            placeholder="e.g. What documents do I need for Anna University CSE?",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_btn:
        send = st.button("Send →", use_container_width=True)

    # ── Process new query ─────────────────────────────────────
    if (send or pending) and user_input.strip():
        augmented_query, intent = process(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("🤔 Thinking…"):
            try:
                result  = ask(chain, augmented_query)
                answer  = result["answer"]
                sources = result.get("source_documents", [])

                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": answer,
                    "intent":  intent,
                    "sources": sources,
                })
                st.rerun()
            except Exception as exc:
                st.error(f"❌ Error calling LLM: {exc}")
