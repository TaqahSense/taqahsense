import time
import json
import pandas as pd
import paho.mqtt.client as mqtt

# File path for cleaned data
CSV_FILE = "cleaned_household_power.csv"

# MQTT Broker settings
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "taqahsense/smart_meter/data"

# Initialize MQTT Client
client = mqtt.Client()

print("Connecting to HiveMQ Broker...")
try:
    client.connect(BROKER, PORT, 60)
    print(f"Connected successfully to {BROKER}:{PORT}")
except Exception as e:
    print(f"Failed to connect to MQTT Broker: {e}")
    exit()

print("Loading cleaned dataset...")
df = pd.read_csv(CSV_FILE)

print(f"Starting real-time streaming to topic '{TOPIC}'...")

# Loop through each row to simulate real-time sensor measurements
for index, row in df.iterrows():
    # Convert row data into a structured JSON payload
    payload = {
        "timestamp": str(row.get("datetime", row.name)),
        "global_active_power": row.get("global_active_power"),
        "global_reactive_power": row.get("global_reactive_power"),
        "voltage": row.get("voltage"),
        "global_intensity": row.get("global_intensity"),
        "sub_metering_1": row.get("sub_metering_1"),
        "sub_metering_2": row.get("sub_metering_2"),
        "sub_metering_3": row.get("sub_metering_3"),
        "sub_metering_4": row.get("sub_metering_4")
    }

    # Convert dictionary to JSON string
    json_data = json.dumps(payload)

    # Publish message to MQTT Broker
    client.publish(TOPIC, json_data)
    print(f"[Sent] Row {index + 1}: {json_data}")

    # Simulate 1-second interval between measurements
    time.sleep(1)

client.disconnect()
print("Data streaming finished.")