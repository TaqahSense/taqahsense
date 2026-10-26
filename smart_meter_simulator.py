import pandas as pd
import time
import json

# Read the cleaned energy dataset
file_path = "cleaned_household_power.csv"
df = pd.read_csv(file_path)

print("Smart Meter Simulator Started...")
print("--------------------------------")

# Simulate live smart meter readings
for _, row in df.iterrows():

    reading = {
        "datetime": row["datetime"],
        "active_power": row["global_active_power"],
        "reactive_power": row["global_reactive_power"],
        "voltage": row["voltage"],
        "current": row["global_intensity"]
    }

    print(json.dumps(reading, indent=2))

    # Send one reading every second
    time.sleep(1)
    