from fastapi import FastAPI, Depends
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import pandas as pd
import os
import pandas as pd
import os
import datetime
import random



# تحديد المسار الدقيق لملف البيانات بجانب ملف api.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'cleaned_commercial_building_power.csv')

app = FastAPI(title="TaqaSense Smart Building API")
# تعريف مفتاح المصادقة الآمن
API_KEY = "taqasense-2026-secret"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: Invalid or missing API Key"
        )
    return api_key

# تحميل البيانات مباشرة من الملف المحفوظ محلياً لضمان سرعة واستقرار الاتصال وعدم الاعتماد على أخطاء الرفع الخارجية
CSV_FILE = 'cleaned_commercial_building_power.csv'

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = df.fillna(0)
        return df
    return pd.DataFrame()

@app.get("/")
def home():
    return {"message": "TaqaSense AI Backend is running successfully!"}

@app.get("/readings")
def get_readings(api_key: str = Security(verify_api_key)):
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



import datetime
import random

@app.post("/run-anomaly-scan")
def run_anomaly_scan(api_key: str = Depends(verify_api_key)):
    """توليد قراءة حية ديناميكية تندمج فوراً مع النظام والفلترة"""
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
        else:
            df = pd.DataFrame()
        
        # استخدام التاريخ الحالي لكي تظهر القراءة الحية ضمن نطاق الداشبورد والفلتر النشط
        new_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # توليد قيم ذكية ومحاكاة دقيقة لمعايير Building Data Genome
        new_row = {
            "timestamp": new_timestamp,
            "global_active_power": round(random.uniform(1.5, 3.2), 2),
            "global_reactive_power": round(random.uniform(0.1, 0.5), 2),
            "voltage": round(random.uniform(228.0, 242.0), 2),
            "global_intensity": round(random.uniform(6.0, 12.0), 2),
            "Kitchen & Cafeteria": round(random.uniform(0.2, 1.5), 2),
            "HVAC Systems": round(random.uniform(1.0, 2.8), 2),
            "Smart Lighting": round(random.uniform(0.1, 0.8), 2),
            "Server Room": round(random.uniform(0.9, 1.8), 2),
            "anomaly": 1  # قراءة طبيعية وآمنة
        }
        
        if not df.empty:
            df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df_updated.to_csv(CSV_FILE, index=False)
            
        return {
            "status": "success", 
            "message": "Live telemetry integrated dynamically across all dashboard modules!",
            "latest_reading": new_row
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))