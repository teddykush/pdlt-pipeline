import os
import requests
import pandas as pd
from sqlalchemy import create_engine

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/"
}

def fetch_nse_live_data():
    session = requests.Session()
    session.headers.update(headers)
    try:
        session.get("https://www.nseindia.com", timeout=10)
        api_url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
        response = session.get(api_url, timeout=10)
        
        # Safely try parsing JSON, catch HTML block pages
        try:
            data = response.json()
            records = data.get("data", [])
            return pd.DataFrame(records)
        except Exception:
            print("NSE block detected: Response is not valid JSON.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Connection error: {e}")
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