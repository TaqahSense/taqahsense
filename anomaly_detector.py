import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_anomalies_with_source():
    print("🤖 Running AI Anomaly Detection with Source Identification...")
    
    # قراءة البيانات المحدثة
    try:
        df = pd.read_csv('cleaned_commercial_building_power.csv')
    except FileNotFoundError:
        print("❌ Error: Cleaned data file not found. Please run clean_data.py first.")
        return

    # الأعمدة الخاصة بالعدادات الفرعية الجديدة
    sub_meters = ['Kitchen & Cafeteria', 'HVAC Systems', 'Smart Lighting', 'Server Room']
    
    # تدريب نموذج Isolation Forest على القدرة الفعالة أو العدادات الفرعية
    features = ['global_active_power'] + sub_meters
    X = df[features]
    
    model = IsolationForest(contamination=0.03, random_state=42)
    df['anomaly'] = model.fit_predict(X)
    
    # تحديد الشذوذ (-1 يعني شذوذ)
    anomalies_df = df[df['anomaly'] == -1].copy()
    
    # دالة لتحديد المصدر بدقة بناءً على أي عداد فرعي سجل أعلى قيمة شاذة
    def identify_source(row):
        values = {col: row[col] for col in sub_meters}
        # العداد الذي يحمل أعلى استهلاك لحظي غالباً هو مصدر الشذوذ أو الحمل الزائد
        max_source = max(values, key=values.get)
        return max_source

    if not anomalies_df.empty:
        anomalies_df['anomaly_source'] = anomalies_df.apply(identify_source, axis=1)
        print(f"⚠️ Detected {len(anomalies_df)} anomalies with identified sources!")
        
        # حفظ النتائج أو عرض عينة منها
        anomalies_df[['timestamp', 'global_active_power', 'anomaly_source']].to_head = anomalies_df.head()
        anomalies_df.to_csv('detected_anomalies_with_sources.csv', index=False)
        print("✅ Anomaly detection results saved to 'detected_anomalies_with_sources.csv'.")
    else:
        print("✨ No anomalies detected in the current window.")

if __name__ == "__main__":
    detect_anomalies_with_source()