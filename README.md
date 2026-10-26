# ⚡ TaqahSense: Cloud-Based Smart Energy & Anomaly Detection System

TaqahSense is an advanced cloud-based smart platform designed to monitor, forecast, and analyze electricity consumption in real-time for commercial facilities and smart cities[cite: 3]. The system addresses energy waste and operational inefficiencies by ingesting time-series energy metrics, leveraging machine learning for anomaly detection, and exposing actionable insights through an interactive role-based dashboard[cite: 3, 13, 18, 29].

---

## 🏗️ System Architecture & Core Layers

The platform follows a modular, cloud-ready architecture:
1. **IoT Simulation Layer:** Simulates smart meters publishing active power, voltage, current, and sub-metering metrics[cite: 21].
2. **Ingestion & Processing Layer:** Validates, cleans, and structures telemetry data before persistence[cite: 22].
3. **Storage Layer (`Supabase`):** Houses structured relational tables and time-series energy records (`energy_readings`)[cite: 30].
4. **AI Analytics Engine (`Isolation Forest`):** Detects electrical surges, leaks, and anomalous spikes in real-time[cite: 22, 34].
5. **Dashboard & API Gateway (`FastAPI` & `Streamlit`):** Delivers live visualization, filtering, and automated decision-support recommendations[cite: 20, 23, 33].

---

## 🛠️ Tech Stack
* **Backend & API:** Python, FastAPI, Uvicorn, Pandas, NumPy[cite: 20, 24]
* **Database & Cloud:** Supabase (PostgreSQL)[cite: 24, 30]
* **Machine Learning:** Scikit-Learn (Isolation Forest)[cite: 24, 34]
* **Frontend & Visualization:** Streamlit[cite: 20, 24]

---

## 🚀 Installation & Local Deployment Guide

Follow these steps to set up and run the project locally:

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/TaqahSense.git](https://github.com/your-username/TaqahSense.git)
cd TaqahSense
2. Install Required Dependencies
Ensure you have Python installed, then run:
pip install -r requirements.txt

3. Configure Environment Variables
Create a .env file in the root directory and add your Supabase credentials:
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
4. Run the Backend Server (FastAPI)
Open a terminal window and start the API:
uvicorn api:app --reload

5. Launch the Interactive Dashboard (Streamlit)
Open a second terminal window and launch the user interface:
streamlit run dashboard.py

👥 Project Team (Jubail Industrial College)
Lolwah Alsubaie   Amjad Alsaud   Sara Alsubaie   Lujain Alfadhel   
