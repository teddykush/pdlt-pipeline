import os
import pandas as pd
import cloudscraper
from sqlalchemy import create_engine

def fetch_nse_live_data():
    scraper = cloudscraper.create_scraper()
    try:
        scraper.get("https://www.nseindia.com", timeout=10)
        api_url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
        response = scraper.get(api_url, timeout=10)
        
        data = response.json()
        
        # Handle cases where the endpoint returns a list directly or a dict containing 'data'
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("data", [])
        else:
            records = []
            
        return pd.DataFrame(records)
    except Exception as e:
        print(f"NSE block or parsing error: {e}")
        return pd.DataFrame()

def run_pipeline():
    df = fetch_nse_live_data()
    if not df.empty:
        database_url = os.environ.get("SUPABASE_URL")
        engine = create_engine(database_url, connect_args={"sslmode": "require"})
        df.to_sql('canonical_nse_records', engine, if_exists='append', index=False)
        print("Successfully updated database.")
    else:
        print("Skipping database write: No valid payload received.")

if __name__ == "__main__":
    run_pipeline()
