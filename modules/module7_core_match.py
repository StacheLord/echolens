# module7_core_match.py

import json
import spacy
from dateutil.parser import parse
from rapidfuzz import fuzz
from urllib.parse import urlparse

nlp = spacy.load("en_core_web_sm")

def normalize_url(url):
    """Normalize URL for comparison (remove query and www.)"""
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return f"{domain}{parsed.path}"

def extract_named_entities(text):
    doc = nlp(text)
    entities = {"PERSON": set(), "GPE": set(), "ORG": set(), "DATE": set()}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].add(ent.text.strip())
    return entities

def compare_entity_overlap(main, other):
    total_matches, total = 0, 0
    for cat in ["PERSON", "GPE", "ORG"]:
        total_matches += len(main[cat] & other[cat])
        total += len(main[cat].union(other[cat]))
    return (total_matches / total * 100) if total else 0

def is_same_event(main, other, entity_threshold=15, title_threshold=60):
    main_entities = extract_named_entities(main["text"])
    other_entities = extract_named_entities(other["text"])
    entity_score = compare_entity_overlap(main_entities, other_entities)

    title_score = fuzz.partial_ratio(
        main.get("title", "").lower(),
        other.get("title", "").lower()
    )

    same_date = None
    main_date = main.get("publish_date")
    other_date = other.get("publish_date")
    invalid_values = ("", None, "None", "null")

    if main_date in invalid_values or other_date in invalid_values:
        print("⚠️ One or both publish dates are missing or invalid — comparing without date proximity.")
    else:
        try:
            m_dt = parse(main_date)
            o_dt = parse(other_date)
            delta = abs((m_dt - o_dt).days)
            same_date = delta <= 14
            print(f"📅 Parsed Dates: {m_dt.date()} vs {o_dt.date()} → Δ {delta} day(s) → Nearby: {same_date}")
        except Exception as e:
            print(f"❌ Date parsing failed: {e}")
            same_date = None

    if same_date is True and (entity_score >= entity_threshold or title_score >= title_threshold):
        verdict = "Likely Same Incident"
    elif entity_score >= entity_threshold or title_score >= title_threshold:
        verdict = "Possibly Related"
    else:
        verdict = "Unlikely Related"

    print(f"\n🔎 Comparing with: {other['title']}")
    print(f" - Entity Score: {round(entity_score, 2)}%")
    print(f" - Title Similarity: {title_score}%")
    print(f" - Date Nearby: {same_date}")
    print(f" - Verdict: {verdict}")

    return {
        "title": other["title"],
        "url": other["url"],
        "entity_score": round(entity_score, 2),
        "title_score": round(title_score, 2),
        "same_date_window": same_date,
        "verdict": verdict
    }

def run_incident_matching(original_path="original_article.json", related_path="related_articles.json", match_results=None):
    with open(original_path, "r", encoding="utf-8") as f:
        main = json.load(f)
    with open(related_path, "r", encoding="utf-8") as f:
        related = json.load(f)

    results = []
    for article in related:
        result = is_same_event(main, article)

        if match_results:
            norm_article_url = normalize_url(article["url"])
            match = next(
                (r for r in match_results if normalize_url(r["source"]) == norm_article_url),
                None
            )
            if match:
                result["matches"] = [
                    {
                        "sentence": m["sentence"],
                        "score": round(m["score"], 2),
                        "phrase": m.get("phrase", "Unknown")
                    }
                    for m in match.get("matches", [])
                ]
            else:
                result["matches"] = []
        else:
            result["matches"] = []

        results.append(result)

    with open("incident_match_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return results
