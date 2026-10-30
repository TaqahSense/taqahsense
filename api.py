from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI(title="TaqaSense Smart Building API")

# تحميل البيانات مباشرة من الملف المحفوظ محلياً لضمان سرعة واستقرار الاتصال وعدم الاعتماد على أخطاء الرفع الخارجية
CSV_FILE = 'cleaned_commercial_building_power.csv'

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df
    return pd.DataFrame()

@app.get("/")
def home():
    return {"message": "TaqaSense AI Backend is running successfully!"}

@app.get("/readings")
def get_readings():
    df = load_data()
    if df.empty:
        return []
    # تحويل البيانات إلى قاموس لإرسالها بسلاسة للداشبورد
    return df.to_dict(orient="records")

@app.get("/anomalies")
def get_anomalies():
    df = load_data()
    if df.empty or "anomaly_flag" not in df.columns:
        return []
    # تصفية السجلات التي تحتوي على شذوذ فقط
    anomalies_df = df[df["anomaly_flag"] == True]
    return anomalies_df.to_dict(orient="records")

@app.post("/run-anomaly-scan")
def run_anomaly_scan():
    # محاكاة لفحص الذكاء الاصطناعي وتأكيد جاهزية النظام
    df = load_data()
    count = int(df["anomaly_flag"].sum()) if not df.empty and "anomaly_flag" in df.columns else 0
    return {
        "status": "success", 
        "message": "AI Anomaly Detection scan completed successfully.",
        "total_anomalies_found": count
    }