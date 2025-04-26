# module1_article_ingestion.py

import json
import logging
import re
from newspaper import Article
from dateutil.parser import parse
from datetime import datetime, timedelta

logging.basicConfig(
    filename='echolens.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_action(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Starting: {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Finished: {func.__name__}")
        return result
    return wrapper

class NewsArticle:
    def __init__(self, url: str):
        self.__url = url
        self.__title = None
        self.__authors = []
        self.__publish_date = None
        self.__text = None
        self.__top_image = None

    @log_action
    def extract(self):
        article = Article(self.__url)
        article.download()
        article.parse()

        self.__title = article.title
        self.__authors = article.authors
        self.__publish_date = str(article.publish_date) if article.publish_date else None
        self.__text = article.text
        self.__top_image = article.top_image

        if not self.__publish_date:
            self.__publish_date = self.extract_date_fallback()
            if self.__publish_date:
                print(f"🗓️ Fallback date from text: {self.__publish_date}")
                logging.info(f"Fallback date from text: {self.__publish_date}")
            else:
                self.__publish_date = self.extract_date_from_url()
                if self.__publish_date:
                    print(f"🗓️ Fallback date from URL: {self.__publish_date}")
                    logging.info(f"Fallback date from URL: {self.__publish_date}")
                else:
                    print(f"⚠️ No publish date found for: {self.__url}")
                    logging.warning(f"No publish date found for: {self.__url}")

        return self

    def extract_date_fallback(self):
        if not self.__text:
            return None

        header_chunk = self.__text[:500]

        # Handle absolute dates
        absolute_patterns = [
            r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}",
            r"\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}",
            r"\b\d{4}-\d{2}-\d{2}"
        ]

        for pattern in absolute_patterns:
            match = re.search(pattern, header_chunk)
            if match:
                try:
                    parsed_date = parse(match.group())
                    return str(parsed_date.date())
                except:
                    continue

        # Handle relative dates like "2 days ago", "5 hours ago"
        rel_pattern = r"(\d+)\s+(day|hour|minute)s?\s+ago"
        match = re.search(rel_pattern, header_chunk, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            unit = match.group(2).lower()
            try:
                if unit == "day":
                    return str((datetime.now() - timedelta(days=num)).date())
                elif unit == "hour":
                    return str((datetime.now() - timedelta(hours=num)).date())
                elif unit == "minute":
                    return str((datetime.now() - timedelta(minutes=num)).date())
            except:
                pass

        return None

    def extract_date_from_url(self):
        match = re.search(r"(\d{4})[/-](\d{2})[/-](\d{2})", self.__url)
        if not match:
            match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", self.__url)
        if match:
            try:
                return str(parse("-".join(match.groups())).date())
            except:
                return None
        return None

    def to_dict(self) -> dict:
        return {
            'url': self.__url,
            'title': self.__title,
            'authors': self.__authors,
            'publish_date': self.__publish_date,
            'text': self.__text,
            'top_image': self.__top_image
        }

    def preview(self, chars=500):
        print(f"\nTitle: {self.title}")
        print(f"Publish Date: {self.publish_date}")
        print(f"Authors: {self.authors}")
        print("\nArticle Text Preview:\n")
        print(self.text[:chars], "...")

    @property
    def url(self): return self.__url
    @property
    def title(self): return self.__title
    @property
    def authors(self): return self.__authors
    @property
    def publish_date(self): return self.__publish_date
    @property
    def text(self): return self.__text
    @property
    def top_image(self): return self.__top_image
