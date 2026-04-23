"""
pages/colleges_tab.py
─────────────────────────────────────────────────────────────────
Renders the Browse Colleges tab:
  - Filterable by location, college type, and stream
  - Expandable cards with full college and course details
  - Shows fees, eligibility, deadlines, and facilities per course
─────────────────────────────────────────────────────────────────
"""

import streamlit as st


# ── Stream detection rules ────────────────────────────────────────
_STREAM_RULES: dict[str, callable] = {
    "Engineering":    lambda n: "B.E" in n or "B.Tech" in n,
    "Medical":        lambda n: any(x in n for x in ["MBBS", "B.D.S", "Nursing"]),
    "Arts & Science": lambda n: "B.Sc" in n or "M.A" in n,
    "Commerce":       lambda n: "B.Com" in n,
}


def _extract_streams(colleges: list) -> set:
    streams = set()
    for c in colleges:
        for course in c["courses"]:
            for stream, rule in _STREAM_RULES.items():
                if rule(course["name"]):
                    streams.add(stream)
    return streams


def _matches_filters(college: dict, sel_loc: str, sel_type: str, sel_stream: str) -> bool:
    if sel_loc    != "All" and college["location"] != sel_loc:
        return False
    if sel_type   != "All" and college["type"]     != sel_type:
        return False
    if sel_stream != "All":
        rule = _STREAM_RULES.get(sel_stream, lambda _: True)
        if not any(rule(c["name"]) for c in college["courses"]):
            return False
    return True


# ── Public renderer ───────────────────────────────────────────────
def render(data: dict) -> None:
    colleges = data["colleges"]

    # ── Filters ───────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        locations = ["All"] + sorted({c["location"] for c in colleges})
        sel_loc   = st.selectbox("📍 Location", locations)
    with col2:
        types    = ["All"] + sorted({c["type"] for c in colleges})
        sel_type = st.selectbox("🏷 College Type", types)
    with col3:
        streams    = _extract_streams(colleges)
        sel_stream = st.selectbox("📚 Stream", ["All"] + sorted(streams))

    # ── Apply filters ─────────────────────────────────────────
    filtered = [c for c in colleges if _matches_filters(c, sel_loc, sel_type, sel_stream)]

    st.markdown(
        f"<p style='color:#64748b;font-size:.85rem;margin-bottom:1rem;'>"
        f"Showing {len(filtered)} college(s)</p>",
        unsafe_allow_html=True,
    )

    # ── College cards ─────────────────────────────────────────
    for college in filtered:
        nirf  = college["ranking"].get("NIRF_2024", "N/A")
        srank = college["ranking"].get("state_rank", "N/A")

        with st.expander(f"🏛 {college['name']} — {college['location']}  |  NIRF #{nirf}"):
            left, right = st.columns(2)

            with left:
                st.markdown(f"""
**Type:** {college['type']}
**Established:** {college['established']}
**Affiliation:** {college['affiliation']}
**NIRF Rank:** {nirf} &nbsp;|&nbsp; **State Rank:** {srank}
**Phone:** {college['contact']['phone']}
**Email:** {college['contact']['email']}
**Address:** {college['contact']['address']}
""")
                pills = " ".join(
                    f'<span class="tag-pill">{f}</span>' for f in college["facilities"]
                )
                st.markdown(f"**Facilities:** {pills}", unsafe_allow_html=True)

            with right:
                for course in college["courses"]:
                    fees  = course["fees"]
                    total = fees["tuition_per_year"] + fees["hostel_per_year"] + fees["other_fees"]
                    st.markdown(
                        f'<div class="info-card">'
                        f'  <h4>📚 {course["name"]}</h4>'
                        f'  <p>⏱ {course["duration"]} &nbsp;|&nbsp; 👥 {course["seats"]} seats</p>'
                        f'  <p>✅ Min: {course["eligibility"]["min_percentage"]}% &nbsp;|&nbsp;'
                        f'     📝 {", ".join(course["eligibility"]["entrance_exams"])}</p>'
                        f'  <p>💰 Tuition: ₹{fees["tuition_per_year"]:,}/yr'
                        f'     &nbsp;|&nbsp; Total ≈ ₹{total:,}/yr</p>'
                        f'  <p>📅 Apply by: <strong style="color:#f97316;">'
                        f'     {course["application"]["end_date"]}</strong></p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
