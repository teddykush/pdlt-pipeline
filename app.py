import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Forensic PDLT Dashboard", layout="wide")

@st.cache_resource
def get_engine():
    return create_engine(st.secrets["SUPABASE_URL"], connect_args={"sslmode": "require"})

engine = get_engine()

@st.cache_data
def load_data():
    df_canon = pd.read_sql("SELECT * FROM canonical_nse_records", engine)
    df_forensic = pd.read_sql("SELECT * FROM nse_attachment_forensics", engine)
    return df_canon, df_forensic

try:
    df_canon, df_forensic = load_data()
    
    st.title("🚨 Forensic Public Disclosure Lag Time (PDLT) Pipeline")
    st.markdown("Live cloud monitoring environment synced with **Supabase PostgreSQL**.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Canonical Records Ingested", len(df_canon))
    col2.metric("Forensic Attachments Logged", len(df_forensic))
    col3.metric("Anomaly Threshold", "> 500 Hours")
    
    st.divider()
    
    st.subheader("📋 Canonical NSE Records (Cloud Database)")
    st.dataframe(df_canon.head(50), use_container_width=True)
    
    st.subheader("🔍 Attachment Forensics & Lag Analysis")
    st.dataframe(df_forensic.head(50), use_container_width=True)

except Exception as e:
    st.error(f"Failed to connect to Supabase cloud database: {e}")