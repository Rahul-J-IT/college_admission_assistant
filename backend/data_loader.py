"""
data_loader.py
─────────────────────────────────────────────────────────────────
Responsibility: Load tn_colleges.json and convert every entity
(college overview, course detail, entrance exam, scholarship) into
LangChain Document objects ready for embedding.

Public API
----------
build_documents() -> List[Document]   # full document list
load_raw_data()   -> dict             # raw JSON (used by UI tabs)
─────────────────────────────────────────────────────────────────
"""

import json
from pathlib import Path
from typing import Dict, List

from langchain_core.documents import Document

from config import DATA_PATH


# ── Raw data loader ───────────────────────────────────────────────
def load_raw_data() -> Dict:
    """Load and return the raw college JSON dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}.\n"
            "Make sure data/tn_colleges.json exists in the project root."
        )
    with open(DATA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── Document builders ─────────────────────────────────────────────
def _college_overview_doc(college: Dict) -> Document:
    text = (
        f"COLLEGE: {college['name']}\n"
        f"Location: {college['location']}\n"
        f"Type: {college['type']}\n"
        f"Established: {college['established']}\n"
        f"Affiliation: {college['affiliation']}\n"
        f"NIRF Ranking 2024: {college['ranking'].get('NIRF_2024', 'N/A')}\n"
        f"State Rank: {college['ranking'].get('state_rank', 'N/A')}\n"
        f"Phone: {college['contact']['phone']}\n"
        f"Email: {college['contact']['email']}\n"
        f"Website: {college['contact']['website']}\n"
        f"Address: {college['contact']['address']}\n"
        f"Facilities: {', '.join(college['facilities'])}"
    )
    return Document(
        page_content=text,
        metadata={
            "college_id":   college["id"],
            "college_name": college["name"],
            "doc_type":     "college_overview",
        },
    )


def _course_detail_doc(college: Dict, course: Dict) -> Document:
    elig = course["eligibility"]

    # Optional cutoff line
    cutoff_line = ""
    for key in ("neet_cutoff", "jee_cutoff", "jee_advanced_cutoff", "viteee_cutoff"):
        if key in elig:
            cutoff_line = f"- Cutoff Info  : {elig[key]}\n"
            break

    docs_block  = "\n".join(f"  - {d}" for d in course["required_documents"])
    quota_block = "\n".join(f"  - {cat}: {pct}" for cat, pct in course["reservation_quota"].items())
    fee_total   = sum(course["fees"].values())

    text = (
        f"COLLEGE : {college['name']} ({college['location']})\n"
        f"COURSE  : {course['name']}\n"
        f"Duration: {course['duration']}  |  Seats: {course['seats']}\n\n"

        f"ELIGIBILITY:\n"
        f"- Minimum Percentage : {elig['min_percentage']}%\n"
        f"- Required Subjects  : {', '.join(elig['required_subjects'])}\n"
        f"- Entrance Exams     : {', '.join(elig['entrance_exams'])}\n"
        f"- Age Limit          : {elig.get('age_limit', 'N/A')}\n"
        f"{cutoff_line}\n"

        f"APPLICATION DATES:\n"
        f"- Start Date  : {course['application']['start_date']}\n"
        f"- Last Date   : {course['application']['end_date']}\n"
        f"- Result Date : {course['application']['result_date']}\n"
        f"- Admission   : {course['application']['admission_date']}\n\n"

        f"FEES (per year):\n"
        f"- Tuition   : Rs. {course['fees']['tuition_per_year']:,}\n"
        f"- Hostel    : Rs. {course['fees']['hostel_per_year']:,}\n"
        f"- Others    : Rs. {course['fees']['other_fees']:,}\n"
        f"- Total     : Rs. {fee_total:,}\n\n"

        f"REQUIRED DOCUMENTS:\n{docs_block}\n\n"

        f"RESERVATION QUOTA:\n{quota_block}"
    )
    return Document(
        page_content=text,
        metadata={
            "college_id":   college["id"],
            "college_name": college["name"],
            "course_id":    course["id"],
            "course_name":  course["name"],
            "doc_type":     "course_detail",
        },
    )


def _entrance_exam_doc(exam_key: str, exam: Dict) -> Document:
    lines = [
        f"ENTRANCE EXAM : {exam['full_name']} ({exam_key})",
        f"Conducted By  : {exam['conducted_by']}",
        f"For Courses   : {exam['for_courses']}",
    ]
    for field in ("pattern", "application_period", "exam_date", "sessions", "eligibility"):
        if field in exam:
            lines.append(f"{field.replace('_', ' ').title()}: {exam[field]}")
    lines.append(f"Official Site : {exam.get('official_site', 'N/A')}")

    return Document(
        page_content="\n".join(lines),
        metadata={"doc_type": "entrance_exam", "exam_key": exam_key},
    )


def _scholarship_doc(sch: Dict) -> Document:
    text = (
        f"SCHOLARSHIP : {sch['name']}\n"
        f"For         : {sch['for']}\n"
        f"Amount      : {sch['amount']}\n"
        f"Eligibility : {sch['eligibility']}"
    )
    return Document(page_content=text, metadata={"doc_type": "scholarship"})


# ── Public entry point ────────────────────────────────────────────
def build_documents() -> List[Document]:
    """
    Convert the full JSON dataset into a flat list of LangChain Documents.
    Called once by pipeline.py during startup.
    """
    data: Dict = load_raw_data()
    docs: List[Document] = []

    for college in data["colleges"]:
        docs.append(_college_overview_doc(college))
        for course in college["courses"]:
            docs.append(_course_detail_doc(college, course))

    for key, exam in data["entrance_exams"].items():
        docs.append(_entrance_exam_doc(key, exam))

    for sch in data["scholarships"]:
        docs.append(_scholarship_doc(sch))

    return docs
