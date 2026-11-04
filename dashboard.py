import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time
import datetime 


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

# الشريط الجانبي للتحكم في التدفق الحي
st.sidebar.markdown("### 🎛️ AI Real-Time Streaming")

# استخدام Session State للتحكم في تشغيل وإيقاف التدفق
if "streaming" not in st.session_state:
    st.session_state.streaming = False

col_start, col_stop = st.sidebar.columns(2)

with col_start:
    if st.button("▶️ Start Live Stream"):
        st.session_state.streaming = True
with col_stop:
    if st.button("⏹️ Stop Stream"):
        st.session_state.streaming = False

# مساحة مخصصة في الشاشة الرئيسية لعرض حالة التدفق الحي اللحظي
stream_placeholder = st.empty()
metrics_placeholder = st.empty()

# إذا كان التدفق مفعلًا، تبدأ الحلقة التكرارية لضخ البيانات أمام اللجنة
if st.session_state.streaming:
    stream_placeholder.info("⚡ Live telemetry stream is active! Sensors are broadcasting data in real-time...")
    
    # حلقة تكرارية لمحاكاة التدفق الحي (تتحدث كل ثانية)
    for _ in range(30):  # يتدفق لمدة 30 قراءة مثلاً أو حتى توقفينه يدوياً
        if not st.session_state.streaming:
            break
            
        try:
            headers = {"X-API-Key": "taqasense-2026-secret"}
            # إرسال طلب السيرفر لتوليد قراءة حية جديدة وتحليلها
            res = requests.post(f"{API_URL}/run-anomaly-scan", headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                latest = data.get('latest_reading', {})
                
                # عرض القراءة الحية المتدفقة لحظياً على الشاشة
                with metrics_placeholder.container():
                    st.toast(f"📡 New Telemetry Ingested: Power = {latest.get('global_active_power')} kW", icon="⚡")
                
                # إعادة تحميل الصفحة لتحديث الرسم البياني والجدول تلقائياً مع كل تدفق
                time.sleep(1.5)  # انتظار ثانية ونصف بين كل قراءة وأخرى لترها اللجنة بوضوح
                st.rerun()
            else:
                st.warning("⚠️ Stream paused: Server returned an error.")
                break
        except Exception as e:
            st.error(f"❌ Stream disconnected: {e}")
            break
else:
    stream_placeholder.success("🟢 System ready. Click 'Start Live Stream' to demonstrate real-time IoT ingestion.")
if st.sidebar.button("🔄 Refresh Dashboard Data"):
    st.rerun()

# جلب البيانات
try:
    headers = {"X-API-Key": "taqasense-2026-secret"}
    readings_res = requests.get(f"{API_URL}/readings", headers=headers).json()
    anomalies_res = requests.get(f"{API_URL}/anomalies", headers=headers).json()
    
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
    max_date = max(pd.to_datetime(all_dates[-1]).date(), datetime.date.today())    
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
    
    # --- التعديل هنا: جعل الجدول يتفاعل مع فلتر السيركت والمقياس المختار ---
    sub_meters = ["Kitchen & Cafeteria", "HVAC Systems", "Smart Lighting", "Server Room"]
    if selected_metric in sub_meters:
        if "circuit" in filtered_anomalies.columns:
            filtered_anomalies = filtered_anomalies[filtered_anomalies["circuit"] == selected_metric]
        else:
            filtered_anomalies = filtered_anomalies[filtered_anomalies[selected_metric] > 7.0]
else:
    filtered_anomalies = df_anomalies
anomaly_count = len(filtered_anomalies)

# ---------------------------------------------------------
# لوحة المؤشرات الرئيسية (مع حل مشكلة اقتطاع النص للمؤشر الرابع)
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
    # حل مشكلة الـ Text Truncation عبر استخدام تصميم HTML مخصص لا ينضغط أبداً
    status_bg = "#d4edda" if anomaly_count == 0 else "#f8d7da"
    status_color = "#155724" if anomaly_count == 0 else "#721c24"
    status_msg = "Stable 🟢" if anomaly_count == 0 else "Attention Required ⚠️"
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 11px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid #e0e0e0;">
            <p style="font-size: 14px; color: #6c757d; margin-bottom: 4px;">🏗️ Building Status</p>
            <p style="font-size: 15px; font-weight: bold; color: {status_color}; background-color: {status_bg}; padding: 4px 8px; border-radius: 4px; display: inline-block; margin: 0;">{status_msg}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# القسم الرئيسي للرسوم البيانية (مع طبقة نقاط الشذوذ الحمراء - Anomaly Overlay)
# ---------------------------------------------------------
st.subheader("📈 Timeline Analysis & Facility Monitoring (with Anomaly Overlay)")

if not filtered_df.empty and selected_metric in filtered_df.columns:
    # إنشاء الرسم البياني باستخدام Plotly لدمج الخط الزمني مع نقاط الشذوذ الحمراء
    fig = go.Figure()

    # 1. رسم خط استهلاك الطاقة الأساسي
    fig.add_trace(go.Scatter(
        x=filtered_df["dt_parsed"], 
        y=filtered_df[selected_metric], 
        mode='lines', 
        name=f'{selected_metric} Trend',
        line=dict(color='#1f77b4', width=2)
    ))

    # 2. إضافة طبقة القيم الشاذة (نقاط حمراء بارزة Scatter markers) إذا وجدت ضمن النطاق
    if not filtered_anomalies.empty and selected_metric in filtered_anomalies.columns:
        fig.add_trace(go.Scatter(
            x=filtered_anomalies["dt_parsed"], 
            y=filtered_anomalies[selected_metric], 
            mode='markers', 
            name='Detected Anomalies',
            marker=dict(color='red', size=11, symbol='circle', line=dict(width=1, color='darkred'))
        ))

    fig.update_layout(
        title=f"Timeline of {selected_metric} with Highlighted Anomalies",
        xaxis_title="Timestamp",
        yaxis_title=selected_metric,
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
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
# التوصيات الذكية ودعم القرار (ديناميكية حسب المتغير المختار أو الشذوذ)
# ---------------------------------------------------------
st.subheader("💡 AI-Driven Actionable Recommendations & Decision Support")

if anomaly_count > 0:
    st.warning(f"⚠️ High energy anomalies detected in the selected date range ({start_str} to {end_str}).")
    
    # توصيات ذكية ديناميكية تتغير حسب المتغير أو نوع الدائرة المختارة في الشريط الجانبي
    if "voltage" in selected_metric.lower():
        st.markdown("""
        * **Voltage Circuit Alert**: Unstable voltage fluctuations detected. Inspect phase balancers, transformer taps, and local power supply quality immediately.
        * **Action**: Coordinate with facilities engineering to log voltage sags and prevent sensitive equipment trip-offs.
        """)
    elif "hvac" in selected_metric.lower() or "cooling" in selected_metric.lower():
        st.markdown("""
        * **HVAC Systems Optimization**: Abnormal cooling load spike detected during off-hours.
        * **Action**: Inspect thermostat schedules, filter pressure drops, and reset compressor setpoints to reduce peak tariff penalties.
        """)
    else:
        st.markdown(f"""
        * **Circuit ({selected_metric})**: Unusual power deviation recorded against baseline patterns.
        * **Action**: Verify automated equipment schedules, check for standby power wastage, and optimize load distribution across active phases.
        """)
else:
    st.success("✅ All commercial facility circuits and sub-metering zones are operating within optimal stability thresholds.")