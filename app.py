import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.set_page_config(layout="wide")
st.title("📊 UPI App Market Dashboard")

# Connect to SQLite DB
db_path = "mydatabase.db"

try:
    conn = sqlite3.connect(db_path)

    # Get available months in sorted order
    months_df = pd.read_sql("SELECT DISTINCT Month FROM upi_apps_data ORDER BY Month", conn)
    available_months = months_df['Month'].tolist()
    selected_month = st.selectbox("🗓️ Select Month", available_months)

    # Convert selected month back to SQL format for filtering
    

    # Load filtered data
    query = f"""
        SELECT * FROM upi_apps_data
        WHERE Month = '{selected_month}'
    """
    df_month = pd.read_sql(query, conn)
    print(df_month.tail(5))
    conn.close()

    # Convert to numeric
    

    # ---------------- KPIs ------------------
    total_volume = df_month['Volume (Mn)'].sum()
    print(total_volume)
    total_value = df_month['Value (Cr)'].sum()
    num_apps = df_month['Application Name'].nunique()
    avg_value_per_app = total_value / num_apps if num_apps else 0

    volume_leader = df_month.loc[df_month['Volume (Mn)'].idxmax()]
    value_leader = df_month.loc[df_month['Value (Cr)'].idxmax()]

    st.subheader(f"📌 Key Metrics for {selected_month}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔁 Total Volume", f"{total_volume:.1f}M", f"{num_apps} Apps")
    col2.metric("💰 Total Value", f"₹{total_value:,.0f}Cr", f"Avg: ₹{avg_value_per_app:,.0f}Cr")
    col3.metric("🏆 Volume Leader", volume_leader['Application Name'], f"{volume_leader['Volume (Mn)']:.1f}M txns")
    col4.metric("💎 Value Leader", value_leader['Application Name'], f"₹{value_leader['Value (Cr)']:,.0f}Cr")

    # ---------------- Derived KPIs ------------------
    df_month['Market Share Volume (%)'] = (df_month['Volume (Mn)'] / total_volume) * 100
    df_month['Market Share Value (%)'] = (df_month['Value (Cr)'] / total_value) * 100
    df_month['Avg Txn Value (₹)'] = (df_month['Value (Cr)'] * 1e7) / (df_month['Volume (Mn)'] * 1e6)

    # ---------------- Data Table ------------------
    st.subheader("📄 Detailed Metrics")
    st.dataframe(df_month[['Application Name', 'Volume (Mn)', 'Value (Cr)',
                           'Market Share Volume (%)', 'Market Share Value (%)', 'Avg Txn Value (₹)']],
                 use_container_width=True)

    # ---------------- Charts ------------------
    st.subheader("📈 Market Share Distribution")

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df_month, names='Application Name', values='Market Share Volume (%)',
                      title='Market Share by Volume')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.pie(df_month, names='Application Name', values='Market Share Value (%)',
                      title='Market Share by Value')
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- Top 5 Apps Bar Chart ------------------
    st.subheader("🏅 Top 5 Apps by Volume (This Month)")
    top_5 = df_month.nlargest(5, 'Volume (Mn)')
    fig_bar = px.bar(top_5.sort_values('Volume (Mn)'), 
                     x='Volume (Mn)', 
                     y='Application Name',
                     orientation='h',
                     text='Volume (Mn)',
                     title=f"Top 5 UPI Apps by Volume – {selected_month}")
    fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_bar.update_layout(yaxis_title="", xaxis_title="Volume (Mn)", height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"❌ Failed to load data:\n{e}")
