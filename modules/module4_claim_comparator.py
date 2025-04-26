# modules/module4_claim_comparator.py

from rapidfuzz import fuzz

def compare_claim_across_articles(claim_input, related_articles, threshold=60, exact_match=False):
    """
    Compare a claim or set of key phrases across related articles.
    Accepts related_articles directly instead of loading from file.
    """

    if not related_articles:
        print("❌ No related articles available for comparison.")
        return []

    # Split input claim string into multiple phrases (by comma or semicolon)
    claim_phrases = [phrase.strip() for phrase in claim_input.replace(";", ",").split(",") if phrase.strip()]
    print(f"\n📌 Comparing against {len(claim_phrases)} key phrase(s): {claim_phrases}\n")

    results = []

    for article in related_articles:
        matches = []
        text = article.get("text", "")

        if not text or len(text.strip()) < 20:
            print(f"⚠️ No usable text found for article: {article.get('title')}")
            results.append({
                "url": article.get("url"),
                "title": article.get("title"),
                "publish_date": article.get("publish_date", "Unknown"),
                "text": text,
                "matches": []
            })
            continue

        sentences = text.split(". ")
        print(f"🔍 Checking article: {article.get('title')}")
        print(f" - Total sentences: {len(sentences)}")

        for sentence in sentences:
            sentence = sentence.strip()
            best_score = 0
            best_phrase = None

            for phrase in claim_phrases:
                if exact_match:
                    # Exact match logic: only score 100% if exact
                    score = 100 if phrase.lower() in sentence.lower() else 0
                else:
                    score = fuzz.partial_ratio(phrase.lower(), sentence.lower())

                if score > best_score:
                    best_score = score
                    best_phrase = phrase

            if best_score >= threshold:
                print(f"✅ Match [{best_score:.2f}%] on \"{best_phrase}\" → {sentence}")
                matches.append({
                    "sentence": sentence,
                    "score": round(best_score, 2),
                    "phrase": best_phrase
                })
            elif best_score > 50:
                print(f"🟡 Partial match (ignored) [{best_score:.2f}%] on \"{best_phrase}\" → {sentence}")

        result = {
            "url": article.get("url"),
            "title": article.get("title"),
            "publish_date": article.get("publish_date", "Unknown"),
            "text": text,
            "matches": matches
        }

        results.append(result)

        if matches:
            print(f"\n📰 {result['title']}")
            for m in matches:
                print(f" - Match [{m['score']:.2f}%] [{m['phrase']}]: {m['sentence']}")
        else:
            print(" - No matches found.")

    return results
