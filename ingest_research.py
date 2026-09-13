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
                "abstract": str(work.get("abstract_inverted_index")),
                "publication_date": work.get("publication_date"),
                "citation_count": work.get("cited_by_count", 0),
                "source_url": work.get("doi") or work.get("id")
            })
        return pd.DataFrame(records)
    return pd.DataFrame()

def save_research_to_db(company_name):
    df = fetch_openalex_research(company_name)
    if not df.empty:
        database_url = os.environ.get("SUPABASE_URL")
        engine = create_engine(database_url, connect_args={"sslmode": "require"})
        df.to_sql('company_research_patents', engine, if_exists='append', index=False)
        print(f"Inserted research records for {company_name}")
    else:
        print(f"No records found for {company_name}")

if __name__ == "__main__":
    targets = ["Reliance", "Tata", "Adani"]
    for target in targets:
        save_research_to_db(target)