# module6b_html_report.py

import os
from datetime import datetime

def generate_html_report(claim, match_results, core_results, fact_check_data=None, manual_sources=None, output_path="report.html"):
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("  <title>EchoLens Report</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; color: #333; }")
    html.append("    h1, h2 { color: #2c3e50; }")
    html.append("    .article { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }")
    html.append("    .verdict { font-weight: bold; }")
    html.append("    .match { margin: 10px 0; padding: 10px; background: #eef; border-left: 4px solid #36c; }")
    html.append("    .note { color: #666; font-style: italic; margin-top: 10px; }")
    html.append("    .factcheck { background: #fff8dc; border-left: 4px solid #e67e22; padding: 15px; margin-bottom: 30px; }")
    html.append("    .header { margin-bottom: 40px; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("  <div class='header'>")
    html.append("    <h1>EchoLens News Comparison Report</h1>")
    html.append(f"    <p><strong>Claim Analyzed:</strong> {claim}</p>")
    html.append(f"    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    html.append("  </div>")

    # FACT-CHECK RESULTS
    html.append("<div class='factcheck'>")
    html.append("<h2>Fact Check Results</h2>")

    if fact_check_data and fact_check_data.get("result"):
        html.append(f"<p><strong>Automated Verdict:</strong> {fact_check_data['result']}</p>")
    else:
        html.append("<p>No automated fact-check verdict available.</p>")

    if manual_sources:
        for name, entries in manual_sources.items():
            html.append(f"<h3>{name}:</h3>")
            if not entries:
                html.append("<p>No results found.</p>")
            else:
                for entry in entries:
                    html.append(f"<p><a href='{entry['url']}' target='_blank'>{entry['url']}</a><br>")
                    html.append(f"Claim: {entry.get('claim', 'N/A')}<br>")
                    html.append(f"Verdict: {entry.get('verdict', 'N/A')}</p>")
    else:
        html.append("<p>No Snopes or PolitiFact results found.</p>")

    html.append("</div>")

    # MATCHED ARTICLES
    for article in core_results:
        html.append("<div class='article'>")
        html.append(f"<h2>{article['title']}</h2>")
        html.append(f"<p><strong>URL:</strong> <a href='{article['url']}' target='_blank'>{article['url']}</a></p>")
        html.append(f"<p><strong>Verdict:</strong> <span class='verdict'>{article['verdict']}</span></p>")
        html.append(f"<p><strong>Entity Score:</strong> {article['entity_score']}% | <strong>Title Score:</strong> {article['title_score']}%</p>")
        html.append(f"<p><strong>Date Nearby:</strong> {article['same_date_window']}</p>")

        if article.get("matches"):
            html.append("<h3>Matching Sentences:</h3>")
            for match in article["matches"]:
                phrase = match.get("phrase", "Unknown trigger")
                html.append(f"<div class='match'>[{phrase}] [{match['score']:.2f}%] {match['sentence']}</div>")
        else:
            html.append("<p class='note'>⚠️ No direct sentence matched the claim, but this article is related based on entity/title/date similarity.</p>")

        html.append("</div>")

    html.append("</body>")
    html.append("</html>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    print(f"✅ HTML report generated: {os.path.abspath(output_path)}")
