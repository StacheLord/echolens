import requests
from bs4 import BeautifulSoup

def search_politifact(claim):
    url = f"https://www.politifact.com/search/?q={claim.replace(' ', '+')}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    for item in soup.select("ul.o-listicle__items li")[:5]:
        title = item.select_one("a.m-statement__quote").text.strip()
        link = "https://www.politifact.com" + item.select_one("a")["href"]
        rating = item.select_one("div.m-statement__meter img")["alt"]
        results.append({"title": title, "url": link, "rating": rating})
    return results

def search_snopes(claim):
    url = f"https://www.snopes.com/search/{claim.replace(' ', '%20')}/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    for article in soup.select("article.media-list__item")[:5]:
        title = article.select_one("h2.title").text.strip()
        link = article.select_one("a")["href"]
        results.append({"title": title, "url": link})
    return results
