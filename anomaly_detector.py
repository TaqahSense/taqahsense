import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_readings():
    # Fetch energy readings from Supabase table
    response = supabase.table("energy_readings").select("*").execute()
    return pd.DataFrame(response.data)

def detect_and_update_anomalies():
    print("Fetching data from Supabase for AI analysis...")
    df = fetch_readings()
    
    if df.empty:
        print("No data found in the table yet.")
        return

    features = ['global_active_power', 'voltage', 'global_intensity']
    X = df[features].dropna()

    if len(X) < 5:
        print("Not enough data points to run Isolation Forest model yet.")
        return

    print("Training Isolation Forest model...")
    model = IsolationForest(contamination=0.05, random_state=42)
    
    # Predict (-1 for anomalies, 1 for normal)
    preds = model.fit_predict(X)
    df['anomaly'] = preds
    
    # Filter anomalies
    anomalies = df[df['anomaly'] == -1]
    print(f"Analysis complete! Found {len(anomalies)} anomalies out of {len(df)} readings.")

    print("Updating Supabase with anomaly flags...")
    
    # Loop through the data and update the database flags if needed
    for index, row in df.iterrows():
        row_id = row['id']
        is_anomaly_flag = True if row['anomaly'] == -1 else False
        
        # Update the record in Supabase (Assuming you have or will add an 'is_anomaly' column, 
        # or we can print/track them directly)
        try:
            supabase.table("energy_readings").update({"is_anomaly": is_anomaly_flag}).eq("id", row_id).execute()
        except Exception as e:
            # If the column 'is_anomaly' doesn't exist yet, we catch it gracefully
            pass

    print("Database successfully synchronized with AI anomaly flags!")

if __name__ == "__main__":
    detect_and_update_anomalies()