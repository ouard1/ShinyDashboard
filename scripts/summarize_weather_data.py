import pandas as pd
import glob
import os
import json
from pymongo import MongoClient
from datetime import datetime


MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "dashboard_app_db"
COLLECTION_NAME = "weather"


def get_region(lat, lon):
    if 37 <= lat <= 49 and -80 <= lon <= -67:
        return "Northeast"
    elif 24 <= lat <= 37 and -125 <= lon <= -102:
        return "Southwest"
    elif 37 <= lat <= 49 and -125 <= lon <= -102:
        return "West"
    elif 24 <= lat <= 37 and -102 <= lon <= -80:
        return "Southeast"
    elif 37 <= lat <= 49 and -102 <= lon <= -80:
        return "Midwest"
    else:
        return "Other"


input_dir = "../data/raw/weather/"

files = glob.glob(os.path.join(input_dir, "*.json"))
all_data = []

for file in files:
    with open(file, "r") as f:
        try:
            data = json.load(f)
            if "hourly" in data:
                hourly_data = data["hourly"]
                for i, time in enumerate(hourly_data["time"]):
                    
                    if "temperature_2m" in hourly_data and "wind_speed_10m" in hourly_data:
                        all_data.append({
                            "timestamp": time,
                            "latitude": data["latitude"],
                            "longitude": data["longitude"],
                            "temperature": hourly_data["temperature_2m"][i],
                            "wind_speed": hourly_data["wind_speed_10m"][i],
                        })
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {file}: {e}")
        except KeyError as e:
            print(f"Missing key in file {file}: {e}")

df = pd.DataFrame(all_data)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["day"] = pd.to_datetime(df["timestamp"].dt.date)
    df["region"] = df.apply(lambda row: get_region(row["latitude"], row["longitude"]), axis=1)

    
    daily_summary = df.groupby(["region", "day"]).agg({
        "temperature": "mean",
        "wind_speed": "max"
    }).reset_index()

    daily_summary["summary_date"] = datetime.now().isoformat()

  
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    documents = daily_summary.to_dict(orient="records")
    collection.insert_many(documents)
    print(f"Inserted {len(documents)} daily summaries into MongoDB collection '{COLLECTION_NAME}' in database '{DB_NAME}'.")

    client.close()
else:
    print("No valid data to process.")
