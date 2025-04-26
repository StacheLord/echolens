import json
import streamlit as st
from modules.module4_claim_comparator import compare_claim_across_articles
from modules.module5_factcheck import fact_check_claim
from modules.module5b_factcheck_scraper import search_politifact, search_snopes
from modules.module7_core_match import run_incident_matching

st.set_page_config(layout="wide", page_title="EchoLens Dashboard")
st.title("EchoLens: News Claim Comparator & Fact Checker")

# Load original article
try:
    with open("original_article.json", "r", encoding="utf-8") as f:
        original = json.load(f)
except FileNotFoundError:
    st.error("No original_article.json found. Please run the main workflow first.")
    st.stop()

st.sidebar.header("Step 1: Enter a Claim")
claim = st.sidebar.text_input("Example: '3 suspects involved'", "")

if not claim:
    st.stop()

st.sidebar.header("Step 2: Select Tools")
run_comparison = st.sidebar.button("Compare Across Articles")
run_factcheck = st.sidebar.checkbox("Check Google Fact Checker")
run_fallbacks = st.sidebar.checkbox("Search PolitiFact + Snopes")

# Preview original article
with st.expander("Original Article"):
    st.markdown(f"**Title:** {original['title']}")
    st.markdown(f"**URL:** {original['url']}")
    st.write(original["text"][:1500] + "...")

# Run comparison and incident verification
if run_comparison:
    st.header("Claim Match Results")
    match_results = compare_claim_across_articles(claim)
    core_results = run_incident_matching()
    verdict_map = {v["url"]: v for v in core_results}

    verdict_filter = st.sidebar.radio("Filter by Match", ("All", "Likely Same Incident", "Possibly Related", "Unlikely Related"))

    for result in match_results:
        url = result["source"]
        verdict = verdict_map.get(url, {}).get("verdict", "Unknown")
        if verdict_filter != "All" and verdict != verdict_filter:
            continue

        color = {"Likely Same Incident": "green", "Possibly Related": "orange", "Unlikely Related": "gray"}.get(verdict, "blue")
        st.subheader(result["title"])
        st.markdown(f"**Verdict:** <span style='color:{color}'>{verdict}</span>", unsafe_allow_html=True)
        st.caption(url)
        for match in result["matches"]:
            st.markdown(f"- **[{match['score']}%]** {match['sentence']}")
        if not result["matches"]:
            st.markdown("*No relevant matches found.*")

if run_factcheck:
    st.header("Google Fact Check")
    g_results = fact_check_claim(claim)
    for res in g_results:
        st.markdown(f"**{res['text']}**")
        for r in res.get("claimReview", []):
            st.markdown(f"- {r['publisher']['name']} – {r.get('text', 'No rating')} – [Link]({r.get('url')})")

if run_fallbacks:
    st.header("Fallback Fact Checks")

    with st.expander("PolitiFact"):
        for r in search_politifact(claim):
            st.markdown(f"**{r['title']}** – {r['rating']} – [Link]({r['url']})")

    with st.expander("Snopes"):
        for r in search_snopes(claim):
            st.markdown(f"**{r['title']}** – [Link]({r['url']})")
