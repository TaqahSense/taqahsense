import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_professional_demo_data():
    print("⚡ Generating professional sliding-window time-series data for TaqaSense...")
    
    # نافذة تشغيلية مدتها 10 أيام تنتهي بتاريخ اليوم المستهدف للمناقشة (29 أكتوبر 2026)
    end_date = datetime(2026, 10, 29, 23, 0, 0)
    start_date = end_date - timedelta(days=10) # تغطي بسلاسة من 19 إلى 29 أكتوبر 2026
    
    timestamps = pd.date_range(start=start_date, end=end_date, freq='h')
    
    np.random.seed(42)
    n = len(timestamps)
    
    df = pd.DataFrame()
    df["timestamp"] = timestamps
    
    # قراءات عامة وفرعية مستقرة وغنية لجميع الأيام لضمان عدم ظهور رسوم بيانية فارغة أبدًا
    df["global_active_power"] = np.random.uniform(2.5, 4.8, n)
    df["global_reactive_power"] = np.random.uniform(0.15, 0.45, n)
    df["voltage"] = np.random.uniform(232.0, 239.0, n)
    df["global_intensity"] = np.random.uniform(12.0, 24.0, n)
    
    df["Kitchen & Cafeteria"] = np.random.uniform(0.8, 1.8, n)
    df["HVAC Systems"] = np.random.uniform(2.2, 4.2, n)
    df["Smart Lighting"] = np.random.uniform(0.3, 0.9, n)
    df["Server Room"] = np.random.uniform(1.2, 2.8, n)
    
    # الحالة الافتراضية طبيعية ومستقرة للجميع (False)
    df["anomaly_flag"] = False
    
    # حقن حالات الشذوذ بدقة حصرياً في يوم العرض (29 أكتوبر 2026) لإبراز كفاءة الذكاء الاصطناعي والتنبيهات
    demo_mask = (df["timestamp"].dt.date == datetime(2026, 10, 29).date())
    anomaly_subset = demo_mask & (df["timestamp"].dt.hour.isin([10, 14, 18, 22])) # ساعات محددة في يوم العرض
    
    if anomaly_subset.sum() > 0:
        count = anomaly_subset.sum()
        df.loc[anomaly_subset, "HVAC Systems"] = np.random.uniform(8.2, 9.9, count)
        df.loc[anomaly_subset, "Server Room"] = np.random.uniform(7.0, 9.0, count)
        df.loc[anomaly_subset, "anomaly_flag"] = True

    df = df.ffill()
    df = df.fillna(value=0.5)
    
    output_filename = 'cleaned_commercial_building_power.csv'
    df.to_csv(output_filename, index=False)
    print(f"✅ Professional sliding window data generated successfully from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}!")

if __name__ == "__main__":
    generate_professional_demo_data()