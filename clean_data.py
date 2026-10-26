import pandas as pd
import numpy as np

print("Generating Commercial Facility Energy Dataset...")

# محاكاة نطاق زمنية لقراءات منشأة تجارية بمعدل كل 15 دقيقة
np.random.seed(42)
date_range = pd.date_range(start="2026-10-01 00:00:00", periods=500, freq="15min")

# أحمال طاقة للمنشأة التجارية بالكيلوواط (kW) تتراوح طبيعياً بين 80 و 180 kW
base_power = np.random.normal(loc=130.0, scale=12.0, size=len(date_range))

# حقن حالات شذوذ متعمدة (Anomalies) مثل ارتفاع مفاجئ في الأحمال أو أحمال خارج أوقات العمل
anomaly_indices = [35, 90, 160, 250, 320, 430]
for idx in anomaly_indices:
    base_power[idx] += np.random.uniform(70.0, 120.0)

df_commercial = pd.DataFrame({
    "timestamp": date_range,
    "global_active_power": np.round(base_power, 2),
    "global_reactive_power": np.round(base_power * 0.18, 2),
    "voltage": np.round(np.random.normal(loc=400.0, scale=2.5, size=len(date_range)), 2), # جهد تجاري 400V
    "global_intensity": np.round(base_power * 1.75, 2),
    "sub_metering_1": np.round(base_power * 0.40, 2), # أحمال التكييف المركزي HVAC
    "sub_metering_2": np.round(base_power * 0.30, 2), # أحمال الإضاءة التجارية Lighting
    "sub_metering_3": np.round(base_power * 0.20, 2), # أحمال السيرفرات والمعدات Main Equipment
    "sub_metering_4": np.round(base_power * 0.10, 2)  # الأحمال المساندة Auxiliary
})

# حفظ الملف الناتج
output_file = "cleaned_commercial_building_power.csv"
df_commercial.to_csv(output_file, index=False)
print(f"✅ Success! Commercial Facility Dataset generated and saved as '{output_file}'.")