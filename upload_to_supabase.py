import os
import pandas as pd
import requests
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY is missing in .env file!")
    exit()

# قراءة ملف بيانات المنشأة التجارية النظيف
csv_file = "cleaned_commercial_building_power.csv"
if not os.path.exists(csv_file):
    print(f"❌ Error: File '{csv_file}' not found. Run clean_data.py first!")
    exit()

df = pd.read_csv(csv_file)
print(f"📦 Loaded {len(df)} records from {csv_file}.")

# رابط جدول القراءات في Supabase (تأكدي من مطابقة اسم الجدول لديكِ، مثل telemetry_metrics_tsdb أو readings)
table_name = "energy_readings" 
url = f"{SUPABASE_URL}/rest/v1/{table_name}"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# تحويل البيانات إلى قائمة من القواميس لرفعها دفعة واحدة
records = df.to_dict(orient="records")

print("🚀 Uploading commercial facility data to Supabase...")
response = requests.post(url, json=records, headers=headers)

if response.status_code in [200, 201]:
    print("✅ Success! Commercial building data uploaded to Supabase successfully.")
else:
    print(f"❌ Failed to upload data. Status: {response.status_code}")
    print(f"Response: {response.text}")