# main_echolens.py

from modules.module1_article_ingestion import NewsArticle
from modules.module2_search_fallback import search_related_articles
from modules.module3_extract_related import extract_related_articles
from modules.module4_claim_comparator import compare_claim_across_articles
from modules.module5_factcheck import fact_check_claim
from modules.module5b_factcheck_scraper import search_politifact, search_snopes
from modules.module6b_html_report import generate_html_report
from modules.module7_core_match import run_incident_matching
import json

def main():
    print("=== EchoLens v1.0 ===")
    url = input("Enter article URL: ").strip()

    # Extract article
    article = NewsArticle(url).extract()
    article.preview()

    # Save original for comparison
    with open("original_article.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(article.to_dict(), indent=4))

    # Search for related URLs
    query = article.title
    related_urls = search_related_articles(query)

    print("\nRelated URLs:")
    for u in related_urls:
        print(f"- {u}")

    # Extract related articles
    extract_related_articles(related_urls)

    # Ask user for claim
    claim = input("\nEnter a specific claim or keywords (comma-separated): ").strip()

    # Compare claim across articles
    match_results = compare_claim_across_articles(claim)

    # Run entity+date/title analysis
    print("\n🔎 Running incident match verification...")
    core_results = run_incident_matching(match_results=match_results)

    # Display summary
    for r in core_results:
        print(f"\n📄 {r['title']}")
        print(f" - Verdict: {r['verdict']}")
        print(f" - Date Match: {r['same_date_window']} | Entity Score: {r['entity_score']}% | Title Score: {r['title_score']}%")
        print(f" - URL: {r['url']}")

        if r.get("matches"):
            print(" - Matching Sentences:")
            for m in r["matches"]:
                print(f"   • [{m.get('phrase', 'unknown')} | {m['score']:.2f}%] {m['sentence']}")
        else:
            print("   • No matching sentences found.")

    # Optional: Fact check
    fact_check_result = None
    politifact_results = []
    snopes_results = []

    if input("\nWould you like to run automated fact checks? (y/n): ").lower() == "y":
        fact_check_result = fact_check_claim(claim)

        print("\nManual fact-check sources:")
        politifact_results = search_politifact(claim)
        snopes_results = search_snopes(claim)

        for source, results in [("PolitiFact", politifact_results), ("Snopes", snopes_results)]:
            print(f"\n🔍 {source} Results:")
            for res in results:
                print(f" - {res['url']}")
                print(f"   Claim: {res.get('claim', 'N/A')}")
                print(f"   Verdict: {res.get('verdict', 'N/A')}")

    # Optional HTML report
    if input("\nGenerate HTML summary report? (y/n): ").lower() == "y":
        generate_html_report(
            claim,
            match_results,
            core_results,
            fact_check_data=fact_check_result,
            manual_sources={
                "PolitiFact": politifact_results,
                "Snopes": snopes_results
            }
        )
        print("✅ Report generated: output_report.html")

if __name__ == "__main__":
    main()
