# module7_core_match.py

import difflib
import datetime
import re
import logging
from dateutil import parser as date_parser
import spacy
nlp = spacy.blank("en")

# --- Utility functions ---

def extract_named_entities(text):
    """Extract named entities like people, locations, organizations from text."""
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in {"PERSON", "ORG", "GPE", "LOC", "EVENT", "LAW"}]

def extract_publish_date(article):
    """Try extracting publish date from article dict."""
    if article.get('publish_date'):
        return article['publish_date']
    if article.get('text'):
        # Try to extract date from article text
        date_match = re.search(r"\b(?:\d{1,2} [A-Z][a-z]{2,8} \d{4}|\d{4}-\d{2}-\d{2})\b", article['text'])
        if date_match:
            try:
                return str(date_parser.parse(date_match.group(0)).date())
            except Exception:
                pass
    if article.get('url'):
        # Try extracting date from URL
        url = article['url']
        date_match = re.search(r"(\d{4})[/-](\d{2})[/-](\d{2})", url)
        if date_match:
            try:
                return str(datetime.date(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))))
            except Exception:
                pass
    return None

def simple_similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

# --- Core function ---

def run_incident_matching(match_results, original_article):
    """Compare original article against related articles to determine same event/incident."""

    core_results = []

    try:
        original_text = original_article.get('text', '')
        original_ents = extract_named_entities(original_text)
        original_date = extract_publish_date(original_article)

        for article in match_results:
            related_text = article.get('text', '')
            related_ents = extract_named_entities(related_text)
            related_date = extract_publish_date(article)

            if not related_text:
                continue

            # Named Entity Overlap Score
            if original_ents and related_ents:
                entity_overlap = len(set(original_ents) & set(related_ents)) / max(len(set(original_ents)), 1)
                entity_score = round(entity_overlap * 100, 2)
            else:
                entity_score = 0.0

            # Title Similarity
            title_score = round(simple_similarity(original_article.get('title', ''), article.get('title', '')) * 100, 2)

            # Date Comparison
            same_date_window = False
            if original_date and related_date:
                try:
                    od = datetime.datetime.strptime(original_date, "%Y-%m-%d").date()
                    rd = datetime.datetime.strptime(related_date, "%Y-%m-%d").date()
                    delta = abs((od - rd).days)
                    same_date_window = delta <= 14
                except Exception as e:
                    logging.warning(f"Date parsing failed: {e}")
            else:
                logging.warning("One or both publish dates missing; skipping strict date comparison.")

            # Verdict
            if entity_score >= 60 and title_score >= 40 and same_date_window:
                verdict = "Likely Same Incident"
            elif (entity_score >= 40 and same_date_window) or (title_score >= 60 and same_date_window):
                verdict = "Possibly Related"
            else:
                verdict = "Unlikely Related"

            article['entity_score'] = entity_score
            article['title_score'] = title_score
            article['same_date_window'] = same_date_window
            article['verdict'] = verdict

            core_results.append(article)

    except Exception as e:
        logging.error(f"Error during incident matching: {e}")

    return core_results
