"""
agent.py
─────────────────────────────────────────────────────────────────
Agentic AI layer — sits between the UI and the RAG chain.

Responsibilities
----------------
1. detect_intent(query)     — classify the user query into a known intent
2. augment_query(q, intent) — enrich the query so the retriever fetches
                              the most relevant chunks for that intent
3. process(query)           — convenience wrapper (detect + augment)
4. INTENT_META              — display metadata (label, badge CSS class)
                              used by the chat UI

Intent taxonomy
---------------
checklist | eligibility | documents | deadlines |
scholarships | fees | comparison | entrance_exam | general
─────────────────────────────────────────────────────────────────
"""

from typing import Tuple


# ── Keyword maps ──────────────────────────────────────────────────
_KEYWORDS: dict[str, list[str]] = {
    "checklist": [
        "checklist", "step by step", "steps to apply", "process",
        "how to apply", "procedure", "what should i do", "guide me",
        "walk me through", "what are the steps",
    ],
    "eligibility": [
        "eligible", "eligibility", "qualify", "can i apply",
        "criteria", "cutoff", "marks required", "minimum marks",
        "percentage needed", "who can apply", "requirements",
    ],
    "documents": [
        "document", "certificate", "what do i need", "required documents",
        "papers needed", "what to bring", "original documents", "what to submit",
    ],
    "deadlines": [
        "deadline", "last date", "when to apply", "dates",
        "application date", "admission date", "schedule", "timeline",
        "closing date", "open date", "when is",
    ],
    "scholarships": [
        "scholarship", "financial aid", "fee waiver", "bursary",
        "stipend", "free seat", "concession", "fee exemption", "financial help",
    ],
    "fees": [
        "fee", "fees", "cost", "how much", "tuition",
        "hostel fee", "total cost", "annual fee", "expensive",
        "affordable", "fee structure", "charges",
    ],
    "comparison": [
        "compare", " vs ", "versus", "better", "difference between",
        "which is best", "rank", "ranking", "best college",
    ],
    "entrance_exam": [
        "exam", "entrance", "tnea", "neet", "jee", "viteee",
        "test", "syllabus", "pattern", "how to crack", "exam date",
    ],
}

_DEFAULT = "general"


# ── Augmentation suffixes ─────────────────────────────────────────
_AUGMENT: dict[str, str] = {
    "checklist": (
        " Provide a complete numbered step-by-step admission checklist "
        "covering: research, eligibility check, entrance exam registration, "
        "application filling, document upload, counselling, fee payment, "
        "and reporting to college."
    ),
    "eligibility": (
        " Include: minimum percentage required, mandatory subjects (PCM/PCB), "
        "entrance exam name, qualifying rank/score, and age limits."
    ),
    "documents": (
        " List every required document — originals and photocopies — including: "
        "mark sheets, community certificate, transfer certificate, "
        "entrance score card, Aadhar card, and any course-specific documents."
    ),
    "deadlines": (
        " Provide all 4 key dates: application start date, last date to apply, "
        "result/rank declaration date, and last date to report to college."
    ),
    "scholarships": (
        " For each scholarship include: name, amount offered, target community/income group, "
        "eligibility criteria, and how/where to apply."
    ),
    "fees": (
        " Break down: tuition fee per year, hostel fee per year, other charges, "
        "and the total annual cost. Mention any fee concession or scholarship available."
    ),
    "comparison": (
        " Provide a side-by-side comparison covering: NIRF ranking, entrance exam required, "
        "total annual fees, seats available, location, and key facilities."
    ),
    "entrance_exam": (
        " Explain: full exam name, conducting body, subject-wise pattern/marks, "
        "application period, official website, and minimum qualifying cutoff."
    ),
    "general": "",
}


# ── Intent display metadata (used by chat UI) ─────────────────────
INTENT_META: dict[str, dict] = {
    "checklist":     {"label": "📋 Checklist",    "badge": "intent-checklist"},
    "eligibility":   {"label": "✅ Eligibility",   "badge": "intent-eligibility"},
    "documents":     {"label": "📄 Documents",     "badge": "intent-documents"},
    "deadlines":     {"label": "📅 Deadlines",     "badge": "intent-deadlines"},
    "scholarships":  {"label": "💰 Scholarships",  "badge": "intent-scholarships"},
    "fees":          {"label": "💳 Fees",           "badge": "intent-fees"},
    "comparison":    {"label": "⚖️ Comparison",    "badge": "intent-comparison"},
    "entrance_exam": {"label": "📝 Entrance Exam", "badge": "intent-exam"},
    "general":       {"label": "💬 General",        "badge": "intent-general"},
}


# ── Public API ────────────────────────────────────────────────────
def detect_intent(query: str) -> str:
    """
    Classify the user query into one of the known intents.
    Uses simple keyword matching — fast and explainable.
    Returns the intent string.
    """
    q = query.lower()
    for intent, keywords in _KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return intent
    return _DEFAULT


def augment_query(query: str, intent: str) -> str:
    """
    Append intent-specific retrieval instructions to the user query.
    This steers the FAISS retriever toward the most relevant chunks.
    """
    suffix = _AUGMENT.get(intent, "")
    return query + suffix if suffix else query


def process(query: str) -> Tuple[str, str]:
    """
    Convenience wrapper — detect intent then augment.

    Returns
    -------
    (augmented_query, intent)
      augmented_query — enriched string to pass to the RAG chain
      intent          — detected intent string (for UI badge)
    """
    intent    = detect_intent(query)
    augmented = augment_query(query, intent)
    return augmented, intent
