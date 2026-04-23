"""
pages/sidebar.py
─────────────────────────────────────────────────────────────────
Renders the Streamlit sidebar:
  - App logo / title
  - Dataset stats (colleges, courses, exams, scholarships)
  - Quick-question shortcut buttons
  - Clear chat button

No API key input — key is loaded from .env via config.py.
─────────────────────────────────────────────────────────────────
"""

import streamlit as st


_QUICK_QUESTIONS = [
    "Show admission checklist for IIT Madras",
    "What documents do I need for MBBS at Madras Medical College?",
    "What is the TNEA 2025 application deadline?",
    "Am I eligible for VIT CSE with 70% marks?",
    "What scholarships are available for SC students?",
    "Compare fees between Anna University and VIT",
    "What entrance exam is required for NIT Trichy?",
    "List all required documents for NEET colleges in TN",
]


def render(data: dict) -> None:
    """Render the full sidebar. Call inside `with st.sidebar:`."""

    # ── Logo / title ──────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:2.5rem;">🎓</div>
            <div style="font-weight:700;font-size:1rem;color:#f97316;">TN Admissions AI</div>
            <div style="font-size:.75rem;color:#64748b;">Groq LLaMA 3 · LangChain · FAISS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Dataset stats ─────────────────────────────────────────
    total_courses = sum(len(c["courses"]) for c in data["colleges"])
    for val, label in [
        (len(data["colleges"]),      "Colleges"),
        (total_courses,               "Courses"),
        (len(data["entrance_exams"]), "Exams"),
        (len(data["scholarships"]),   "Scholarships"),
    ]:
        st.markdown(
            f'<div class="metric-card">'
            f'  <div class="metric-value">{val}</div>'
            f'  <div class="metric-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")

    # ── Quick questions ───────────────────────────────────────
    st.markdown(
        "<p style='color:#94a3b8;font-size:.8rem;font-weight:600;"
        "text-transform:uppercase;letter-spacing:.05em;'>⚡ Quick Questions</p>",
        unsafe_allow_html=True,
    )
    for q in _QUICK_QUESTIONS:
        if st.button(q, key=f"qq_{q[:25]}", use_container_width=True):
            st.session_state["pending_question"] = q

    st.markdown("---")

    # ── Clear chat ────────────────────────────────────────────
    if st.button("🗑  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        chain = st.session_state.get("rag_chain")
        if chain:
            chain.memory.clear()
        st.rerun()
