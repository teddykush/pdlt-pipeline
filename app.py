import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Connect to Supabase
engine = create_engine(st.secrets["SUPABASE_URL"], connect_args={"sslmode": "require"})

st.subheader("🔍 Industrial Finance Linguistic Search Engine")
search_term = st.text_input("Enter financial term or keyword (e.g., restructuring, default, capex):")

if search_term:
    try:
        with engine.connect() as conn:
            # Pull all records and filter in pandas to avoid database column mismatch errors
            df_all = pd.read_sql(text("SELECT * FROM canonical_nse_records"), conn)
            
        if not df_all.empty:
            # Search case-insensitively across all columns and rows
            mask = df_all.astype(str).apply(lambda col: col.str.contains(search_term, case=False, na=False)).any(axis=1)
            df_results = df_all[mask]
            
            if not df_results.empty:
                st.success(f"Found {len(df_results)} matching corporate targets for: **{search_term}**")
                st.dataframe(df_results, use_container_width=True)
            else:
                st.warning("No matching corporate announcements found for this specific term.")
        else:
            st.warning("The database table is currently empty.")
    except Exception as e:
        st.error(f"Search query error: {e}")
