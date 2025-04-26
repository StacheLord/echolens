import json
from modules.module1_article_ingestion import NewsArticle

def extract_related_articles(url_list):
    extracted = []
    for url in url_list:
        try:
            article = NewsArticle(url).extract()
            extracted.append(article.to_dict())
        except:
            pass
    with open("related_articles.json", "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=4)
    return extracted
