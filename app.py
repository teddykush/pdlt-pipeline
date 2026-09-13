import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Connect to Supabase
engine = create_engine(st.secrets["SUPABASE_URL"], connect_args={"sslmode": "require"})

st.subheader("🔍 Industrial Finance Linguistic Search Engine")
search_term = st.text_input("Enter financial term or keyword (e.g., restructuring, default, capex):")

if search_term:
    query = text("""
        SELECT * FROM canonical_nse_records 
        WHERE cast(desc as text) ILIKE :term 
           OR cast(subject as text) ILIKE :term
    """)
    try:
        with engine.connect() as conn:
            df_results = pd.read_sql(query, conn, params={"term": f"%{search_term}%"})
            
        if not df_results.empty:
            st.success(f"Found {len(df_results)} matching corporate targets for: **{search_term}**")
            st.dataframe(df_results, use_container_width=True)
        else:
            st.warning("No matching corporate announcements found for this specific term.")
    except Exception as e:
        st.error(f"Search query error: {e}")
