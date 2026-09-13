import requests
import pandas as pd
from sqlalchemy import create_engine
import os

# 1. Establish session to bypass NSE bot detection headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

def fetch_nse_live_data():
    session = requests.Session()
    session.headers.update(headers)
    
    # Hit the main NSE homepage first to grab the required tracking cookies
    session.get("https://www.nseindia.com", timeout=10)
    
    # Now query the target NSE data API endpoint safely
    api_url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    response = session.get(api_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        print(f"Failed to fetch NSE data: Status code {response.status_code}")
        return pd.DataFrame()

# 2. Push fetched records to Supabase
def run_pipeline():
    df = fetch_nse_live_data()
    if not df.empty:
        database_url = os.environ.get("SUPABASE_URL")
        engine = create_engine(database_url, connect_args={"sslmode": "require"})
        # Append data to your cloud database
        df.to_sql('canonical_nse_records', engine, if_exists='append', index=False)
        print("Successfully updated database with live NSE records.")

if __name__ == "__main__":
    run_pipeline()