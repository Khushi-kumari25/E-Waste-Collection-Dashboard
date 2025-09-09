import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide", page_title="E-Waste Collection Dashboard")

# --- Sample Data ---
SAMPLE_DATA = [
    {"date":"2025-08-01","device":"Mobile","weight_kg":0.2,"material_type":"Battery","region":"North"},
    {"date":"2025-08-02","device":"Old Laptop","weight_kg":2.5,"material_type":"Metal","region":"South"},
    {"date":"2025-08-05","device":"Plastic Toy","weight_kg":0.5,"material_type":"Plastic","region":"East"},
    {"date":"2025-08-10","device":"TV","weight_kg":15.0,"material_type":"Metal","region":"South"},
]

def load_data(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame(SAMPLE_DATA)
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()

st.title("📊 E-Waste Collection Dashboard")

uploaded = st.sidebar.file_uploader("Upload your E-Waste data (CSV/Excel)", type=['csv','xlsx'])
df = load_data(uploaded)

df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce').fillna(0)
df['material_type'] = df['material_type'].fillna('Other')

total_waste = df['weight_kg'].sum()
by_material = df.groupby('material_type')['weight_kg'].sum().sort_values(ascending=False)
top_material = by_material.index[0] if not by_material.empty else "N/A"
top_region = df.groupby('region')['weight_kg'].sum().idxmax() if not df.empty else "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Total E-Waste (kg)", f"{total_waste:.2f}")
col2.metric("Top Material", top_material)
col3.metric("Top Region", top_region)

st.markdown("---")

if not df.empty:
    monthly = df.set_index('date').resample('M')['weight_kg'].sum().reset_index()
    monthly['month'] = monthly['date'].dt.strftime('%Y-%m')
    fig_line = px.line(monthly, x='month', y='weight_kg', markers=True, title="Monthly E-Waste (kg)")
    st.plotly_chart(fig_line, use_container_width=True)

    fig_pie = px.pie(df, names='material_type', values='weight_kg', title="Material Share")
    st.plotly_chart(fig_pie, use_container_width=True)

    fig_bar = px.bar(df, x='region', y='weight_kg', title="Region-wise Collection", color='region')
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Raw Data")
st.dataframe(df)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Cleaned CSV", data=csv, file_name="ewaste_data.csv", mime="text/csv")
