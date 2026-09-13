import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Forensic PDLT Dashboard", layout="wide")

@st.cache_resource
def get_engine():
    return create_engine(st.secrets["SUPABASE_URL"], connect_args={"sslmode": "require"})

engine = get_engine()

# ---> UPDATE THIS SECTION <---
@st.cache_data(ttl=600)  # Add (ttl=600) right here inside the decorator
def load_data():
    df_canon = pd.read_sql("SELECT * FROM canonical_nse_records", engine)
    df_forensic = pd.read_sql("SELECT * FROM nse_attachment_forensics", engine)
    return df_canon, df_forensic

try:
    df_canon, df_forensic = load_data()
    # ... rest of your dashboard code ...
    df_canon, df_forensic = load_data()
    
    st.title("🚨 Forensic Public Disclosure Lag Time (PDLT) Pipeline")
    st.markdown("Live cloud monitoring environment synced with **Supabase PostgreSQL**.")
    
    # Sidebar Controls & Filters
    st.sidebar.header("🔍 Controls & Filters")
    threshold = st.sidebar.slider("Anomaly Threshold (Hours)", min_value=100, max_value=2000, value=500, step=50)
    
    # Top KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Canonical Records", len(df_canon))
    col2.metric("Forensic Records", len(df_forensic))
    col3.metric("Active Threshold", f"{threshold} Hrs")
    
    st.divider()
    
    # Visual Analytics Section
    st.subheader("📊 Lag-Time Distribution Analytics")
    if not df_forensic.empty and any(col in df_forensic.columns for col in ['lag_time_hours', 'lag_hours', 'delay_hours']):
        # Automatically detect the lag column name
        lag_col = next(col for col in ['lag_time_hours', 'lag_hours', 'delay_hours'] if col in df_forensic.columns)
        st.bar_chart(df_forensic[lag_col])
    else:
        st.info("Forensic dataset loaded successfully. Reviewing raw metrics below.")
    
    st.divider()
    
    # Data Tables
    st.subheader("📋 Canonical NSE Records")
    st.dataframe(df_canon.head(100), use_container_width=True)
    
    st.subheader("🔍 Attachment Forensics")
    st.dataframe(df_forensic.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Dashboard runtime error: {e}")
