import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FACT_CHECK_API_KEY")

def fact_check_claim(claim_text):
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": claim_text, "key": API_KEY, "languageCode": "en-US", "pageSize": 5}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("claims", [])
