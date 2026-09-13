import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(st.secrets["SUPABASE_URL"], connect_args={"sslmode": "require"})

st.subheader("🌐 Unified Financial Intelligence & Research Platform")

tab1, tab2 = st.tabs(["NSE Regulatory Risks", "Correlated Research & Patents"])

with tab1:
    search_term = st.text_input("Search financial risk terms (e.g., default, restructuring):")
    if search_term:
        with engine.connect() as conn:
            df_all = pd.read_sql(text("SELECT * FROM canonical_nse_records"), conn)
        if not df_all.empty:
            mask = df_all.astype(str).apply(lambda col: col.str.contains(search_term, case=False, na=False)).any(axis=1)
            st.dataframe(df_all[mask], use_container_width=True)

with tab2:
    company_query = st.text_input("Search corporate research/patents by company name:")
    if company_query:
        query = text('SELECT * FROM company_research_patents WHERE company_name ILIKE :name')
        with engine.connect() as conn:
            df_patents = pd.read_sql(query, conn, params={"name": f"%{company_query}%"})
        if not df_patents.empty:
            st.success(f"Found {len(df_patents)} research/patent records.")
            st.dataframe(df_patents, use_container_width=True)
        else:
            st.warning("No records found for this company.")