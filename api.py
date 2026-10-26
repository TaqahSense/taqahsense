import os
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="TaqahSense API", description="Energy Monitoring and Anomaly Detection Backend")

@app.get("/")
def read_root():
    return {"message": "Welcome to TaqahSense API - Backend is running successfully!"}

@app.get("/readings")
def get_energy_readings():
    response = supabase.table("energy_readings").select("*").limit(50).execute()
    return response.data

@app.get("/anomalies")
def get_anomalies():
    response = supabase.table("energy_readings").select("*").eq("anomaly_flag", True).execute()
    return response.data

@app.get("/summary")
def get_summary():
    return {
        "status": "System Healthy",
        "prediction_status": "LSTM Time-Series model ready for energy forecasting"
    }