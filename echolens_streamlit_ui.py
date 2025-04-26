# echolens_streamlit_ui.py

import streamlit as st
import json
import os
import io
from datetime import datetime
from collections import defaultdict
import spacy
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import difflib
from difflib import SequenceMatcher
import re
import pandas as pd
from urllib.parse import quote_plus

from modules.module1_article_ingestion import NewsArticle
from modules.module2_search_fallback import search_related_articles
from modules.module3_extract_related import extract_related_articles
from modules.module4_claim_comparator import compare_claim_across_articles
from modules.module5_factcheck import fact_check_claim
from modules.module5b_factcheck_scraper import search_politifact, search_snopes
from modules.module7_core_match import run_incident_matching

# Load Spacy model safely
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# Streamlit setup
st.set_page_config(page_title="EchoLens", layout="wide")
st.title("🧠 EchoLens News Comparison Dashboard")

ps = PorterStemmer()

# Initialize session state
for key in ["original_article", "related_articles", "match_results", "core_results", "fact_checks"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- Step 1: Enter URL ---
st.header("📥 Step 1: Enter Article URL")
article_url = st.text_input("Paste the URL of the article you want to analyze:")
run_extraction = st.button("Extract and Analyze")

if run_extraction and article_url:
    with st.spinner("Extracting original article..."):
        article = NewsArticle(article_url).extract()
        st.session_state.original_article = article.to_dict()

    with st.spinner("Searching for related articles..."):
        related_urls = search_related_articles(article.title)
        if len(related_urls) < 5:
            relaxed_query = " ".join(article.title.split()[:6])
            relaxed_urls = search_related_articles(relaxed_query)
            related_urls = list(set(related_urls + relaxed_urls))
        st.session_state.related_articles = extract_related_articles(related_urls)

    st.success(f"✅ Found and extracted {len(related_urls)} related articles.")

# --- Step 2: Claim Matching ---
# --- Step 2: Claim Matching ---
st.header("🧩 Step 2: Enter Claim or Keywords")
claim_input = st.text_input("Enter key phrases (e.g., 'Trump AND Ukraine OR Musk'):", "Trump AND Ukraine OR Musk")
exact_match = st.toggle("Require Exact Match", value=False)
threshold = st.slider("Match Threshold", 50, 100, 60)
run_match = st.button("Run Analysis")

if run_match and claim_input:
    with st.spinner("Running claim comparison and incident matching..."):
        st.session_state.match_results = compare_claim_across_articles(
            claim_input,
            st.session_state.related_articles,
            threshold=threshold if not exact_match else 100,
            exact_match=exact_match
        )
        st.session_state.core_results = run_incident_matching(
            st.session_state.match_results,
            st.session_state.original_article
        )
    st.success("✅ Matching complete.")

# --- Step 3: Explore Results ---
if st.session_state.core_results:
    st.header("📊 Step 3: Explore Results")
    st.sidebar.header("Filters")

    verdict_filter = st.sidebar.selectbox("Verdict", ["All", "Likely Same Incident", "Possibly Related", "Unlikely Related"])
    entity_range = st.sidebar.slider("Entity Score Range", 0, 100, (0, 100))
    title_range = st.sidebar.slider("Title Score Range", 0, 100, (0, 100))
    date_filter = st.sidebar.selectbox("Date Nearby", ["All", True, False])
    score_filter = st.sidebar.slider("Min Sentence Match Score", 0, 100, 60)

    phrases = sorted({m.get("phrase", "Unknown") for a in st.session_state.core_results for m in a.get("matches", [])})
    phrase_filter = st.sidebar.multiselect("Trigger Keywords", phrases)

    def filter_articles(data):
        filtered = []
        for article in data:
            if verdict_filter != "All" and article['verdict'] != verdict_filter:
                continue
            if not (entity_range[0] <= article['entity_score'] <= entity_range[1]):
                continue
            if not (title_range[0] <= article['title_score'] <= title_range[1]):
                continue
            if date_filter != "All" and article['same_date_window'] != date_filter:
                continue
            matches = [m for m in article.get("matches", [])
                       if m['score'] >= score_filter and (not phrase_filter or m.get('phrase') in phrase_filter)]
            if matches or verdict_filter != "Unlikely Related":
                a = article.copy()
                a['matches'] = matches
                filtered.append(a)
        return filtered

    
    for a in filter_articles(st.session_state.core_results):
        with st.expander(f"{a['title']} [{a['verdict']}]"):
            st.write(f"**URL**: [{a['url']}]({a['url']})")
            st.write(f"**Entity Score**: {a['entity_score']}% | **Title Score**: {a['title_score']}%")
            st.write(f"**Date Nearby**: {a['same_date_window']}")
            if a.get("matches"):
                for m in a['matches']:
                    st.markdown(f"- [`{m.get('phrase', '?')}` | {m['score']}%] {m['sentence']}")
            else:
                st.info("No sentence matches found.")

# --- Visual Diff Tool ---
if st.session_state.core_results and len(st.session_state.core_results) >= 2:
    st.header("📝 Visual Diff Between Two Articles (Strict Fact-Pair Matching)")

    titles = [f"{a['title'][:80]}..." for a in st.session_state.core_results]
    a_idx = st.selectbox("Select Article A", options=range(len(titles)), format_func=lambda i: titles[i])
    b_idx = st.selectbox("Select Article B", options=range(len(titles)), format_func=lambda i: titles[i], index=1)

    max_delta = st.slider("Maximum Allowed Numeric Difference", min_value=1, max_value=20, value=5, step=1)

    def get_text(article):
        text = article.get("text", "")
        if not text:
            text = "\n".join(m["sentence"] for m in article.get("matches", []))
        return text

    text_a = get_text(st.session_state.core_results[a_idx])
    text_b = get_text(st.session_state.core_results[b_idx])

    def normalize_tokens(text):
        return re.findall(r"\w+|%+", text.lower())

    def extract_sentences(text):
        return re.split(r'(?<=[.!?]) +', text)

    def extract_fact_pairs(text):
        fact_pairs = []
        for sentence in extract_sentences(text):
            tokens = normalize_tokens(sentence)
            for i in range(len(tokens)-1):
                if re.match(r"\d+%?", tokens[i]):
                    fact_pairs.append((sentence.strip(), tokens[i], ps.stem(tokens[i+1])))
                elif re.match(r"\d+%?", tokens[i+1]):
                    fact_pairs.append((sentence.strip(), tokens[i+1], ps.stem(tokens[i])))
        return fact_pairs

    def number_to_int(n):
        n = n.replace("%", "")
        try:
            return int(n)
        except:
            return None

    facts_a = extract_fact_pairs(text_a)
    facts_b = extract_fact_pairs(text_b)

    matched_a = set()
    matched_b = set()
    unmatched_a = set(facts_a)
    unmatched_b = set(facts_b)

    for (sent_a, num_a, kw_a) in facts_a:
        n_a = number_to_int(num_a)
        if n_a is not None:
            for (sent_b, num_b, kw_b) in facts_b:
                n_b = number_to_int(num_b)
                if n_b is not None:
                    if kw_a == kw_b and abs(n_a - n_b) <= max_delta:
                        matched_a.add((sent_a, num_a, kw_a))
                        matched_b.add((sent_b, num_b, kw_b))
                        unmatched_a.discard((sent_a, num_a, kw_a))
                        unmatched_b.discard((sent_b, num_b, kw_b))

    def highlight_facts(text, matches, unmatched):
        for (sentence, num, keyword) in matches:
            pattern = re.escape(num) + r'.{0,30}' + re.escape(keyword)
            text = re.sub(pattern, lambda m: f"<span class='matched'>{m.group(0)}</span>", text, flags=re.IGNORECASE)
        for (sentence, num, keyword) in unmatched:
            pattern = re.escape(num) + r'.{0,30}' + re.escape(keyword)
            text = re.sub(pattern, lambda m: f"<span class='unmatched'>{m.group(0)}</span>", text, flags=re.IGNORECASE)
        return text

    st.markdown("""
    <style>
    span.matched {
        background-color: #7ed957;
        padding: 2px;
        border-radius: 4px;
    }
    span.unmatched {
        background-color: #ffd699;
        padding: 2px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    highlighted_a = highlight_facts(text_a, matched_a, unmatched_a)
    highlighted_b = highlight_facts(text_b, matched_b, unmatched_b)

    st.markdown("### 📰 Original Article", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #ccc; padding:10px; max-height:400px; overflow:auto;'>{highlighted_a}</div>", unsafe_allow_html=True)
    st.markdown("### 📰 Comparison Article", unsafe_allow_html=True)
    st.markdown(f"<div style='border:1px solid #ccc; padding:10px; max-height:400px; overflow:auto;'>{highlighted_b}</div>", unsafe_allow_html=True)

