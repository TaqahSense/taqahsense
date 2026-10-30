import streamlit as st
import pandas as pd
import requests

# إعدادات صفحة الداشبورد
st.set_page_config(
    page_title="TaqaSense Smart Building Energy Dashboard",
    page_icon="⚡",
    layout="wide"
)

# تصميم عصري ونظيف
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TaqaSense - AI-Powered Smart Building Energy & Decision Support System")
st.markdown("---")

API_URL = "http://127.0.0.1:8000"

# الشريط الجانبي للتحكم
st.sidebar.markdown("### 🎛️ AI Model Control")
if st.sidebar.button("🚀 Run Live Anomaly Detection Scan"):
    try:
        res = requests.post(f"{API_URL}/run-anomaly-scan")
        if res.status_code == 200:
            st.sidebar.success("AI Scan Completed Successfully!")
            st.rerun()
        else:
            st.sidebar.warning("Scan triggered.")
    except Exception:
        st.sidebar.error("Backend unreachable.")

if st.sidebar.button("🔄 Refresh Dashboard Data"):
    st.rerun()

# جلب البيانات
try:
    readings_res = requests.get(f"{API_URL}/readings").json()
    anomalies_res = requests.get(f"{API_URL}/anomalies").json()
    
    df_readings = pd.DataFrame(readings_res)
    df_anomalies = pd.DataFrame(anomalies_res)
    
    if not df_readings.empty and "timestamp" in df_readings.columns:
        df_readings["dt_parsed"] = pd.to_datetime(df_readings["timestamp"], errors='coerce')
        df_readings = df_readings.dropna(subset=["dt_parsed"])
        df_readings["date_str"] = df_readings["dt_parsed"].dt.strftime('%Y-%m-%d')

    if not df_anomalies.empty and "timestamp" in df_anomalies.columns:
        df_anomalies["dt_parsed"] = pd.to_datetime(df_anomalies["timestamp"], errors='coerce')
        df_anomalies = df_anomalies.dropna(subset=["dt_parsed"])
        df_anomalies["date_str"] = df_anomalies["dt_parsed"].dt.strftime('%Y-%m-%d')

except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Advanced Filters")

available_metrics = [
    col for col in [
        "global_active_power", "global_reactive_power", "voltage", "global_intensity", 
        "Kitchen & Cafeteria", "HVAC Systems", "Smart Lighting", "Server Room"
    ] 
    if not df_readings.empty and col in df_readings.columns
]

selected_metric = st.sidebar.selectbox(
    "Select Power Metric / Circuit:", 
    available_metrics if available_metrics else ["global_active_power"]
)

if not df_readings.empty and "date_str" in df_readings.columns:
    all_dates = sorted(df_readings["date_str"].unique())
    min_date = pd.to_datetime(all_dates[0]).date()
    max_date = pd.to_datetime(all_dates[-1]).date()
    
    date_range = st.sidebar.date_input("Filter by Date Range:", value=(min_date, max_date))
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d = end_d = date_range if not isinstance(date_range, tuple) else date_range[0]
        
    start_str = start_d.strftime('%Y-%m-%d')
    end_str = end_d.strftime('%Y-%m-%d')
    
    mask = (df_readings["date_str"] >= start_str) & (df_readings["date_str"] <= end_str)
    filtered_df = df_readings.loc[mask]
else:
    filtered_df = df_readings
    start_str = end_str = None

if not df_anomalies.empty and "date_str" in df_anomalies.columns and start_str and end_str:
    mask_anomalies = (df_anomalies["date_str"] >= start_str) & (df_anomalies["date_str"] <= end_str)
    filtered_anomalies = df_anomalies.loc[mask_anomalies]
else:
    filtered_anomalies = df_anomalies

anomaly_count = len(filtered_anomalies)

# ---------------------------------------------------------
# لوحة المؤشرات الرئيسية
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Filtered Readings", len(filtered_df))
with col2:
    st.metric("⚠️ Detected Anomalies", anomaly_count, delta=f"-{anomaly_count}" if anomaly_count > 0 else "Stable", delta_color="inverse")
with col3:
    total_power = round(filtered_df[selected_metric].sum(), 2) if not filtered_df.empty and selected_metric in filtered_df.columns else 0
    st.metric("⚡ Total Metric Load", f"{total_power} kW")
with col4:
    status_text = "Stable 🟢" if anomaly_count == 0 else "Attention ⚠️"
    st.metric("🏗️ Building Status", status_text)

st.markdown("---")

# ---------------------------------------------------------
# القسم الرئيسي للرسوم البيانية (عُدل إلى خطوط بسيطة ونظيفة كما طلبتِ)
# ---------------------------------------------------------
st.subheader("📈 Timeline Analysis & Facility Monitoring")
if not filtered_df.empty and selected_metric in filtered_df.columns:
    chart_data = filtered_df.set_index("dt_parsed")[selected_metric]
    # إرجاع الرسم البياني إلى خطوط بسيطة وواضحة (Line Chart)
    st.line_chart(chart_data, use_container_width=True)
else:
    st.info("No data available for the selected metric and date range.")

st.markdown("---")

# عرض استهلاك الـ Sub-meters بشكل منظم
st.subheader("🏢 Sub-Metering Power Distribution Overview")
sub_meters = ["HVAC Systems", "Server Room", "Kitchen & Cafeteria", "Smart Lighting"]
available_sub_meters = [m for m in sub_meters if not filtered_df.empty and m in filtered_df.columns]

if not filtered_df.empty and available_sub_meters:
    sub_cols = st.columns(len(available_sub_meters))
    for i, sm in enumerate(available_sub_meters):
        avg_val = round(filtered_df[sm].mean(), 2)
        with sub_cols[i]:
            st.metric(sm, f"{avg_val} kW")
else:
    st.info("No sub-metering breakdown available.")

st.markdown("---")

# ---------------------------------------------------------
# جدول حالات الشذوذ المكتشفة
# ---------------------------------------------------------
st.subheader("⚠️ Latest Detected Anomalies with Sources & Timestamp:")
if not filtered_anomalies.empty:
    st.dataframe(filtered_anomalies, use_container_width=True)
else:
    st.success("✅ No anomalies detected for the selected date range. Facility is operating normally.")

st.markdown("---")

# ---------------------------------------------------------
# التوصيات الذكية ودعم القرار
# ---------------------------------------------------------
st.subheader("💡 AI-Driven Actionable Recommendations & Decision Support")
if anomaly_count > 0:
    st.warning(f"⚠️ High energy anomalies detected in the selected date range ({start_str} to {end_str}). Recommended actions:")
    st.markdown("""
    * **HVAC Systems**: Inspect cooling load schedules and thermostat setpoints immediately.
    * **Server Room**: Verify cooling efficiency and airflow distribution.
    * **Kitchen & Cafeteria**: Monitor peak-hour equipment usage and reduce standby power draws.
    """)
else:
    st.success("✅ All commercial facility circuits and sub-metering zones are operating within optimal stability thresholds.")