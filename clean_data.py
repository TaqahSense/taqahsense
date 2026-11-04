import pandas as pd
import numpy as np
from datetime import datetime

def generate_bdg_october_data():
    print("⚡ Generating BDG-simulated October time-series data for TaqaSense...")
    
    # تغطية شهر أكتوبر بالكامل (من 1 أكتوبر إلى 31 أكتوبر 2026) بدقة تاعة
    start_date = datetime(2026, 10, 1, 0, 0, 0)
    end_date = datetime(2026, 10, 31, 23, 59, 59)
    
    timestamps = pd.date_range(start=start_date, end=end_date, freq='h')
    n = len(timestamps)
    
    np.random.seed(42)
    
    # محاكاة سلوك أحمال المباني التجارية (BDG style: تذبذب جيبه يومي يعكس ساعات العمل والذروة)
    daily_cycle = np.sin(np.linspace(0, n * 2 * np.pi / 24, n))
    base_load = 3.0 + 1.2 * np.maximum(0, daily_cycle)
    
    df = pd.DataFrame()
    df["timestamp"] = timestamps
    
    # المقاييس الرئيسية بتوزيع يحاكي قراءات العدادات الحقيقية
    df["global_active_power"] = np.clip(base_load + np.random.normal(0, 0.3, n), 1.5, 6.0)
    df["global_reactive_power"] = np.random.uniform(0.15, 0.45, n)
    df["voltage"] = np.random.normal(232.0, 1.5, n)
    df["global_intensity"] = df["global_active_power"] * 4.2
    
    # الأحمال الفرعية (Sub-Metering) بمحاكاة واقعية لبيانات BDG
    df["Kitchen & Cafeteria"] = np.clip(0.8 + 0.5 * np.maximum(0, daily_cycle) + np.random.normal(0, 0.1, n), 0.5, 2.5)
    df["HVAC Systems"] = np.clip(2.0 + 1.8 * np.maximum(0, daily_cycle) + np.random.normal(0, 0.2, n), 1.0, 5.5)
    df["Smart Lighting"] = np.clip(0.4 + 0.2 * np.abs(daily_cycle) + np.random.normal(0, 0.05, n), 0.2, 1.0)
    df["Server Room"] = np.random.uniform(1.5, 2.2, n) # استهلاك ثابت ومستقر للسيرفرات
    
    # الحالة الافتراضية طبيعية ومستقرة للجميع (False / 0)
    df["anomaly_flag"] = False
    df["is_anomaly"] = 0
    df["circuit"] = "HVAC Systems" # الدائرة الافتراضية
    df["smart_recommendation"] = "Normal Operation - Optimal Efficiency."

    # حقن حالات الشذوذ بشكل متنوع ودقيق للأيام (10، 20، 30) لأجهزة مختلفة
    # 1. اليوم 10: شذوذ في نظام التكييف (HVAC Systems)
    mask_10 = (df["timestamp"].dt.day == 10) & (df["timestamp"].dt.hour.isin([14, 15, 16]))
    if mask_10.sum() > 0:
        c10 = mask_10.sum()
        df.loc[mask_10, "HVAC Systems"] = np.random.uniform(8.5, 9.8, c10)
        df.loc[mask_10, "anomaly_flag"] = True
        df.loc[mask_10, "is_anomaly"] = 1
        df.loc[mask_10, "circuit"] = "HVAC Systems"
        df.loc[mask_10, "smart_recommendation"] = "⚠️ HVAC Load Spike: Abnormal thermal surge during peak hours. Action: Inspect thermostat schedules and optimize compressor setpoints."

    # 2. اليوم 20: شذوذ في غرفة السيرفرات (Server Room)
    mask_20 = (df["timestamp"].dt.day == 20) & (df["timestamp"].dt.hour.isin([12, 13, 14]))
    if mask_20.sum() > 0:
        c20 = mask_20.sum()
        df.loc[mask_20, "Server Room"] = np.random.uniform(7.5, 9.2, c20)
        df.loc[mask_20, "anomaly_flag"] = True
        df.loc[mask_20, "is_anomaly"] = 1
        df.loc[mask_20, "circuit"] = "Server Room"
        df.loc[mask_20, "smart_recommendation"] = "🔥 Server Room Thermal Alert: High power draw and cooling strain detected. Action: Verify CRAC unit airflow, check rack load balancing, and clear ventilation paths."

    # 3. اليوم 30: شذوذ في المطبخ والكافتيريا (Kitchen & Cafeteria)
    mask_30 = (df["timestamp"].dt.day == 30) & (df["timestamp"].dt.hour.isin([11, 12, 13]))
    if mask_30.sum() > 0:
        c30 = mask_30.sum()
        df.loc[mask_30, "Kitchen & Cafeteria"] = np.random.uniform(6.5, 8.5, c30)
        df.loc[mask_30, "anomaly_flag"] = True
        df.loc[mask_30, "is_anomaly"] = 1
        df.loc[mask_30, "circuit"] = "Kitchen & Cafeteria"
        df.loc[mask_30, "smart_recommendation"] = "⚡ Kitchen Equipment Surge: Simultaneous heavy appliance usage detected. Action: Stagger commercial oven and dishwasher operating cycles to prevent phase imbalance."

    df = df.ffill()
    df = df.fillna(value=0.5)
    
    output_filename = 'cleaned_commercial_building_power.csv'
    df.to_csv(output_filename, index=False)
    print(f"✅ BDG-mimicked October dataset generated successfully ({n} records)!")

if __name__ == '__main__':
    generate_bdg_october_data()