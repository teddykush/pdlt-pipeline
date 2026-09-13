import os
import requests
import pandas as pd
from sqlalchemy import create_engine

def fetch_openalex_research(company_name):
    url = f"https://api.openalex.org/works?search={company_name}&per-page=10"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json().get("results", [])
        records = []
        for work in data:
            records.append({
                "company_name": company_name,
                "entity_type": "research",
                "title": work.get("title"),
                "abstract": work.get("abstract_inverted_index"), # Can be parsed or stored as-is
                "publication_date": work.get("publication_date"),
                "citation_count": work.get("cited_by_count", 0),
                "source_url": work.get("doi") or work.get("id")
            })
        return pd.DataFrame(records)
    return pd.DataFrame()