# module2_search_fallback.py

from googlesearch import search
from urllib.parse import urlparse
import logging

# Logging config
logging.basicConfig(
    filename='echolens.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Curated list of known major news outlets
news_domains = [
    "cnn.com", "reuters.com", "bbc.com", "nytimes.com", "foxnews.com", "apnews.com",
    "npr.org", "nbcnews.com", "abcnews.go.com", "cbsnews.com", "washingtonpost.com",
    "theguardian.com", "forbes.com", "bloomberg.com", "usatoday.com", "latimes.com",
    "politico.com", "newsweek.com", "msnbc.com", "thehill.com", "aljazeera.com",
    "time.com", "pbs.org", "wsj.com", "economist.com", "axios.com", "buzzfeednews.com",
    "vice.com", "independent.co.uk", "telegraph.co.uk", "globalnews.ca", "cbc.ca",
    "ctvnews.ca", "abc.net.au", "smh.com.au", "japantimes.co.jp", "stripes.com",
    "dw.com", "lemonde.fr", "haaretz.com", "timesofisrael.com"
]

def get_domain(url):
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc

def search_related_articles(query, num_results=20):
    print(f"\n🔍 Searching for related articles on: \"{query}\"")
    results = []
    seen_domains = set()

    try:
        for url in search(query, num_results=num_results):
            domain = get_domain(url)
            print(f"Found: {url}")

            if not any(known in domain for known in news_domains):
                print(f"✗ Filtered (not in approved list): {domain}")
                continue

            if domain in seen_domains:
                print(f"✗ Skipped duplicate domain: {domain}")
                continue

            print(f"✓ Accepted [{domain}]: {url}")
            results.append(url)
            seen_domains.add(domain)

    except Exception as e:
        logging.error(f"Search failed: {e}")
        print("[ERROR] Search failed. See echolens.log for details.")

    print(f"\n✅ Total accepted, unique-domain results: {len(results)}")
    return results

