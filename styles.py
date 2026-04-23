"""
styles.py
─────────────────────────────────────────────────────────────────
All custom CSS for the Streamlit app.
Call inject_styles() once in app.py immediately after set_page_config().
─────────────────────────────────────────────────────────────────
"""

import streamlit as st


def inject_styles() -> None:
    """Inject the full CSS stylesheet into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Design tokens ───────────────────────────────────────────── */
:root {
    --accent:   #f97316;
    --accent2:  #3b82f6;
    --surface:  #0f172a;
    --surface2: #1e293b;
    --text:     #e2e8f0;
    --subtext:  #94a3b8;
    --muted:    #64748b;
    --border:   rgba(255,255,255,0.08);
}

html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1a1f3a 50%, #0f172a 100%);
    color: var(--text);
}

/* ── Page header ─────────────────────────────────────────────── */
.main-header {
    background: linear-gradient(135deg, #1e293b, #1a1f3a);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute; top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(249,115,22,.15) 0%, transparent 70%);
    pointer-events: none;
}
.header-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(90deg, #f97316, #fb923c, #fbbf24);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0; line-height: 1.2;
}
.header-subtitle {
    color: var(--subtext); font-size: .95rem; margin-top: .5rem; font-weight: 300;
}

/* ── Info cards ──────────────────────────────────────────────── */
.info-card {
    background: rgba(30,41,59,.7);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.info-card h4 {
    color: var(--accent); font-size: .85rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .08em; margin: 0 0 .6rem;
}
.info-card p, .info-card li { color: var(--subtext); font-size: .88rem; margin: .25rem 0; }

/* ── Intent badges ───────────────────────────────────────────── */
.intent-badge {
    display: inline-block; padding: .25rem .75rem; border-radius: 999px;
    font-size: .75rem; font-weight: 600; letter-spacing: .05em;
    text-transform: uppercase; margin-bottom: .5rem;
}
.intent-checklist    { background: rgba(34,197,94,.15);  color: #22c55e; border: 1px solid rgba(34,197,94,.3); }
.intent-eligibility  { background: rgba(59,130,246,.15); color: #3b82f6; border: 1px solid rgba(59,130,246,.3); }
.intent-documents    { background: rgba(168,85,247,.15); color: #a855f7; border: 1px solid rgba(168,85,247,.3); }
.intent-deadlines    { background: rgba(249,115,22,.15); color: #f97316; border: 1px solid rgba(249,115,22,.3); }
.intent-scholarships { background: rgba(234,179,8,.15);  color: #eab308; border: 1px solid rgba(234,179,8,.3); }
.intent-fees         { background: rgba(239,68,68,.15);  color: #ef4444; border: 1px solid rgba(239,68,68,.3); }
.intent-comparison   { background: rgba(20,184,166,.15); color: #14b8a6; border: 1px solid rgba(20,184,166,.3); }
.intent-exam         { background: rgba(99,102,241,.15); color: #818cf8; border: 1px solid rgba(99,102,241,.3); }
.intent-general      { background: rgba(148,163,184,.15);color: #94a3b8; border: 1px solid rgba(148,163,184,.3); }

/* ── Chat bubbles ────────────────────────────────────────────── */
.chat-user {
    background: linear-gradient(135deg, rgba(249,115,22,.15), rgba(251,146,60,.08));
    border: 1px solid rgba(249,115,22,.25);
    border-radius: 12px 12px 4px 12px;
    padding: 1rem 1.2rem; margin: .75rem 0; margin-left: 10%;
}
.chat-ai {
    background: rgba(30,41,59,.8);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 1rem 1.2rem; margin: .75rem 0; margin-right: 5%;
}
.chat-label { font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .5rem; }
.label-user { color: #f97316; }
.label-ai   { color: #3b82f6; }

/* ── Checklist ───────────────────────────────────────────────── */
.checklist-wrap {
    background: rgba(30,41,59,.6);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem;
}
.checklist-step {
    display: flex; align-items: flex-start; gap: .75rem;
    padding: .6rem 0; border-bottom: 1px solid var(--border);
}
.checklist-step:last-child { border-bottom: none; }
.step-num {
    background: linear-gradient(135deg, #f97316, #fb923c);
    color: #fff; font-size: .75rem; font-weight: 700;
    width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-text { color: var(--text); font-size: .9rem; line-height: 1.4; }

/* ── Tag pills ───────────────────────────────────────────────── */
.tag-pill {
    display: inline-block;
    background: rgba(59,130,246,.12); color: #60a5fa;
    border: 1px solid rgba(59,130,246,.25);
    padding: .2rem .6rem; border-radius: 999px;
    font-size: .75rem; margin: .2rem .1rem;
}

/* ── Sidebar ─────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0d1526 !important;
    border-right: 1px solid var(--border);
}

/* ── Inputs ──────────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(30,41,59,.9) !important;
    border: 1px solid rgba(249,115,22,.3) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Sora', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 2px rgba(249,115,22,.15) !important;
}

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important; padding: .6rem 1.5rem !important;
    transition: all .2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(249,115,22,.4) !important;
}

/* ── Misc ────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }
.source-doc {
    background: rgba(15,23,42,.8); border-left: 3px solid #3b82f6;
    padding: .6rem .8rem; border-radius: 0 8px 8px 0; margin: .4rem 0;
    font-size: .8rem; color: var(--subtext); font-family: 'JetBrains Mono', monospace;
}
.metric-card {
    background: rgba(30,41,59,.7); border: 1px solid var(--border);
    border-radius: 10px; padding: .9rem; text-align: center; margin-bottom: .75rem;
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #f97316; line-height: 1; }
.metric-label { font-size: .7rem; color: var(--subtext); text-transform: uppercase; letter-spacing: .06em; margin-top: .3rem; }
.deadline-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: .6rem 1rem; background: rgba(30,41,59,.5);
    border: 1px solid rgba(255,255,255,.06); border-radius: 8px; margin: .3rem 0;
}
</style>
"""
