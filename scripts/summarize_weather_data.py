import pandas as pd
import glob
import os
import json
import re
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
    try:
       
        match = re.search(r"weather_data_(\-?\d+)_\-(\d+)_", file)
        lat, lon = None, None
        if match:
            lat, lon = float(match.group(1)), -float(match.group(2))  


        with open(file, "r") as f:
            data = json.load(f)
            
            
            if not lat or not lon:
                lat, lon = data.get("latitude"), data.get("longitude")
            
            
            if "hourly" in data:
                hourly_data = data["hourly"]
                
                for i, time in enumerate(hourly_data["time"]):
                    temperature = hourly_data.get("temperature_2m", [None])[i]
                    wind_speed = hourly_data.get("wind_speed_10m", [None])[i]
                    
                    
                    if temperature is not None and wind_speed is not None:
                        all_data.append({
                            "timestamp": time,
                            "latitude": lat,
                            "longitude": lon,
                            "temperature": temperature,
                            "wind_speed": wind_speed,
                        })
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file}: {e}")
    except KeyError as e:
        print(f"Missing key in file {file}: {e}")
    except Exception as e:
        print(f"Unexpected error processing file {file}: {e}")


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

    
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted file: {file}")
        except OSError as e:
            print(f"Error deleting file {file}: {e}")
    client.close()
else:
    print("No valid data to process.")
