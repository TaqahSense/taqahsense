import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import subprocess

# Page Configuration
st.set_page_config(
    page_title="TaqahSense Smart Building Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Title & Header
st.title("⚡ TaqahSense - AI-Powered Smart Building Energy & Decision Support System")
st.markdown("---")

# API Base URL
API_URL = "http://127.0.0.1:8000"

# Sidebar Control Panel
st.sidebar.header("⚙️ Smart Control Panel")

# 1. زر تفاعلي لتشغيل الفحص الذكي من داخل الداشبورد مباشرة
st.sidebar.subheader("🤖 AI Model Control")
if st.sidebar.button("🚀 Run Live Anomaly Detection Scan"):
    with st.spinner("Executing AI model and updating database..."):
        try:
            subprocess.run(["python", "anomaly_detector.py"], check=True)
            st.sidebar.success("AI Scan Completed Successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Failed to run scan: {e}")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Dashboard Data"):
    st.rerun()

# Fetching Data from FastAPI Backend
try:
    readings_res = requests.get(f"{API_URL}/readings").json()
    anomalies_res = requests.get(f"{API_URL}/anomalies").json()
    
    df_readings = pd.DataFrame(readings_res)
    df_anomalies = pd.DataFrame(anomalies_res)
    
    # تحويل عمود الوقت إلى تاريخ ووقت حقيقي للتصفية
    if not df_readings.empty and "timestamp" in df_readings.columns:
        df_readings["timestamp"] = pd.to_datetime(df_readings["timestamp"])
    
    # ---------------------------------------------------------
    # الفلاتر التفاعلية المتقدمة في الشريط الجانبي
    # ---------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Advanced Filters")
    
    # أ. فلتر اختيار العداد أو خط التغذية (Sub-metering / Metrics)
    available_metrics = [col for col in ["global_active_power", "global_reactive_power", "voltage", "global_intensity", "sub_metering_1", "sub_metering_2", "sub_metering_3", "sub_metering_4"] if col in df_readings.columns]
    selected_metric = st.sidebar.selectbox("Select Power Metric / Circuit:", available_metrics if available_metrics else ["global_active_power"])

    # ب. فلتر نطاق التاريخ والوقت (Date/Time Range Filter)
    if not df_readings.empty:
        min_date = df_readings["timestamp"].dt.date.min()
        max_date = df_readings["timestamp"].dt.date.max()
        
        date_range = st.sidebar.date_input(
            "Filter by Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df_readings = df_readings[
                (df_readings["timestamp"].dt.date >= start_date) & 
                (df_readings["timestamp"].dt.date <= end_date)
            ]

    # 1. Key Performance Indicators (KPIs)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Filtered Facility Readings", len(df_readings))
    with col2:
        st.metric("Detected Facility Anomalies ⚠️", len(df_anomalies))
    with col3:
        status_text = "⚠️ Immediate Action Required" if len(df_anomalies) > 0 else "✅ Facility Stable"
        st.metric("Building Health Status", status_text)
        
    st.markdown("---")

    # 2. AI-Driven Actionable Recommendations & Decision Support
    st.subheader("💡 AI-Driven Actionable Recommendations & Decision Support")
    
    if not df_anomalies.empty:
        st.warning("⚠️ **Smart Alert:** Abnormal power surges detected in the facility. Automated decision support active.")
        
        latest_anomaly = df_anomalies.iloc[0]
        timestamp_anomaly = latest_anomaly.get("timestamp", "N/A")
        power_val = latest_anomaly.get("global_active_power", 0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.error(f"**Anomaly Timestamp:** {timestamp_anomaly}")
            st.markdown(f"- **Active Power Spike:** `{power_val} kW`")
            st.markdown("- **Diagnosis:** Potential equipment overload or unauthorized after-hours usage.")
        with c2:
            st.success("**Automated Corrective Actions Proposed:**")
            st.markdown("1. **Isolate Circuit:** Automatically isolate sub-metering zone.")
            st.markdown("2. **Load Shedding:** Reduce non-essential HVAC/Lighting power.")
            st.markdown("3. **Dispatch Maintenance:** Send instant alert to facility engineers.")
    else:
        st.success("✅ **All Systems Normal:** Building energy consumption operates within optimal AI-predicted thresholds.")

    st.markdown("---")

    # 3. Interactive Energy Consumption & Circuit Filtering Chart
    st.subheader(f"📈 Timeline Analysis: {selected_metric.replace('_', ' ').title()}")
    
    if not df_readings.empty:
        fig = px.line(
            df_readings, 
            x="timestamp", 
            y=selected_metric, 
            title=f"Facility Monitoring - {selected_metric.replace('_', ' ').title()}",
            labels={selected_metric: "Power Value", "timestamp": "Timestamp"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # 4. Detailed Anomalies Log Table
    st.subheader("📋 Facility Anomalies & Audit Log")
    if not df_anomalies.empty:
        st.dataframe(df_anomalies, use_container_width=True)
    else:
        st.success("No anomaly logs found for the selected criteria.")

except Exception as e:
    st.error(f"Connection Error: Ensure FastAPI server (uvicorn) is running. Details: {e}")
    