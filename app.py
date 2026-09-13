import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Forensic PDLT Dashboard", layout="wide")

@st.cache_resource
def get_engine():
    return create_engine(st.secrets["SUPABASE_URL"], connect_args={"sslmode": "require"})

engine = get_engine()

@st.cache_data(ttl=600)
def load_data():
    df_canon = pd.read_sql("SELECT * FROM canonical_nse_records", engine)
    df_forensic = pd.read_sql("SELECT * FROM nse_attachment_forensics", engine)
    return df_canon, df_forensic

try:
    df_canon, df_forensic = load_data()
    
    st.title("🚨 Forensic Public Disclosure Lag Time (PDLT) Pipeline")
    st.markdown("Live cloud monitoring environment synced with **Supabase PostgreSQL**.")
    
    # Sidebar Controls & Filters
    st.sidebar.header("🔍 Controls & Filters")
    threshold = st.sidebar.slider("Anomaly Threshold (Hours)", min_value=100, max_value=2000, value=500, step=50)
    
    # Identify lag column dynamically
    lag_col = next((col for col in ['lag_time_hours', 'lag_hours', 'delay_hours'] if col in df_forensic.columns), None)
    
    # Filter anomalies if lag column exists
    if lag_col:
        anomalies_df = df_forensic[df_forensic[lag_col] > threshold]
    else:
        anomalies_df = pd.DataFrame()

    # Top KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Canonical Records", len(df_canon))
    col2.metric("Forensic Records", len(df_forensic))
    col3.metric("Anomalies Flagged", len(anomalies_df) if lag_col else "N/A", delta=f"> {threshold} Hrs")
    
    st.divider()
    
    # Visual Analytics Section
    st.subheader("📊 Lag-Time Distribution Analytics")
    if not df_forensic.empty and lag_col:
        st.bar_chart(df_forensic[lag_col])
    else:
        st.info("Forensic dataset loaded successfully.")
    
    st.divider()
    
    # Data Tables with Anomaly Focus
    st.subheader(f"⚠️ Flagged Anomalies (> {threshold} Hours)")
    if not anomalies_df.empty:
        st.dataframe(anomalies_df, use_container_width=True)
    else:
        st.success("No anomalies detected above the current threshold.")
        
    st.subheader("📋 Canonical NSE Records")
    st.dataframe(df_canon.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Dashboard runtime error: {e}")
