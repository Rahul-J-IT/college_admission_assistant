"""
pages/checklist_tab.py
─────────────────────────────────────────────────────────────────
Renders the Checklist tab:
  - College selector (general or specific)
  - 13-step admission checklist
  - Universal document checklist
  - 2025 key deadline table
─────────────────────────────────────────────────────────────────
"""

import streamlit as st


# ── Static data ───────────────────────────────────────────────────
_STEPS = [
    ("Research Colleges",
     "Explore TN colleges based on your stream, budget, and location. "
     "Compare NIRF rankings, facilities, and placement records."),
    ("Check Eligibility",
     "Verify minimum percentage, required subjects (PCM / PCB), "
     "age limits, and special category cutoffs for your chosen courses."),
    ("Register for Entrance Exam",
     "Register for the right exam: TNEA (Engineering), NEET-UG (Medical), "
     "JEE Main/Advanced (NITs/IITs), or VITEEE (VIT)."),
    ("Prepare & Appear for Exam",
     "Write the entrance exam. Preserve your Hall Ticket. "
     "Download your rank/score card once results are declared."),
    ("Fill Online Application",
     "Visit the official college / counselling portal and fill the "
     "application form carefully with correct personal and academic details."),
    ("Upload Required Documents",
     "Scan and upload: 10th & 12th marksheets, Community Certificate, "
     "Transfer Certificate, Aadhar Card, Passport Photos, Entrance Score Card."),
    ("Pay Application Fee",
     "Pay via Net Banking / UPI / Debit Card. Save the payment confirmation."),
    ("Attend Counselling",
     "Participate in centralised counselling (e.g., TNEA Counselling) "
     "or institution-level counselling. Lock your college and course choice."),
    ("Receive Allotment Letter",
     "Download and print the seat allotment / provisional admission letter "
     "from the official portal."),
    ("Report to College on Due Date",
     "Visit the college on the reporting date with ALL original documents "
     "and fees. Complete physical document verification."),
    ("Pay Tuition & Hostel Fees",
     "Pay required fees at the college finance office. Store all receipts."),
    ("Medical Check-up",
     "Undergo the mandatory medical fitness examination at the college health centre."),
    ("Collect ID & Attend Orientation",
     "Collect your student ID card. Attend the induction / orientation programme."),
]

_UNIVERSAL_DOCS = [
    "10th Standard Mark Sheet (Original + 2 Photocopies)",
    "12th Standard Mark Sheet (Original + 2 Photocopies)",
    "Transfer Certificate from previous institution",
    "Community Certificate (issued by Tahsildar)",
    "Nativity Certificate",
    "Aadhar Card (Original + 2 Photocopies)",
    "Passport Size Photographs (minimum 10)",
    "Medical Fitness Certificate",
    "Income Certificate (for scholarship / fee concession)",
    "Entrance Exam Score Card (TNEA / NEET / JEE / VITEEE)",
    "Conduct / Character Certificate from previous institution",
]

_DEADLINES = [
    ("VITEEE Application",        "Oct 2024 – Mar 2025",   "VIT Vellore",             "✅ Closed"),
    ("JEE Main Session 1",        "Jan 2025",              "NITs, IIITs, GFTIs",      "✅ Done"),
    ("JEE Main Session 2",        "Apr 2025",              "NITs, IIITs, GFTIs",      "🟡 Recent"),
    ("JEE Advanced",              "Apr 15 – May 15, 2025", "IITs",                    "🟡 Active"),
    ("NEET-UG",                   "Feb – Mar 2025",        "Medical Colleges TN",     "🟡 Recent"),
    ("TNEA Application",          "Apr 1 – Jun 30, 2025",  "Engineering Colleges TN", "🟢 Open"),
    ("Loyola / Private Colleges", "Mar – May 2025",        "Minority / Private",      "🟡 Varies"),
    ("MKU / State Universities",  "May 1 – Jun 30, 2025",  "Arts & Science / PG",     "🟢 Open"),
]


# ── Public renderer ───────────────────────────────────────────────
def render(data: dict) -> None:
    col1, col2 = st.columns([2, 1])
    with col1:
        college_names = ["General (All Colleges)"] + [c["name"] for c in data["colleges"]]
        selected      = st.selectbox("Choose College (optional)", college_names)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        _ = st.selectbox("Your Stream", ["Engineering", "Medical", "Arts & Science", "Commerce"])

    label = None if selected == "General (All Colleges)" else selected
    _render_steps(label)

    st.markdown("<br>", unsafe_allow_html=True)
    _render_doc_checklist()

    st.markdown(
        "<h3 style='color:#f97316;font-size:1rem;margin-top:1.5rem;'>📅 Important 2025 Deadlines</h3>",
        unsafe_allow_html=True,
    )
    _render_deadlines()


# ── Private helpers ───────────────────────────────────────────────
def _render_steps(college_name: str | None) -> None:
    title = (
        f"📋 Admissions Checklist — {college_name}"
        if college_name
        else "📋 General TN College Admissions Checklist"
    )
    st.markdown('<div class="checklist-wrap">', unsafe_allow_html=True)
    st.markdown(
        f"<h3 style='color:#f97316;margin-bottom:1rem;font-size:1.1rem;'>{title}</h3>",
        unsafe_allow_html=True,
    )
    for i, (step_title, step_desc) in enumerate(_STEPS, 1):
        st.markdown(
            f'<div class="checklist-step">'
            f'  <div class="step-num">{i}</div>'
            f'  <div class="step-text">'
            f'    <strong style="color:#e2e8f0;">{step_title}</strong><br>'
            f'    <span style="color:#94a3b8;font-size:.85rem;">{step_desc}</span>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_doc_checklist() -> None:
    items = "".join(f"<p>✅ {doc}</p>" for doc in _UNIVERSAL_DOCS)
    st.markdown(
        f'<div class="info-card"><h4>📄 Universal Document Checklist</h4>{items}</div>',
        unsafe_allow_html=True,
    )


def _render_deadlines() -> None:
    for name, dates, scope, status in _DEADLINES:
        st.markdown(
            f'<div class="deadline-row">'
            f'  <span style="color:#e2e8f0;font-size:.88rem;font-weight:600;">{name}</span>'
            f'  <span style="color:#94a3b8;font-size:.82rem;">{dates}</span>'
            f'  <span style="color:#64748b;font-size:.8rem;">{scope}</span>'
            f'  <span style="font-size:.8rem;">{status}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
