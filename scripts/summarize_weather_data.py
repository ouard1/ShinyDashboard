import pandas as pd
import glob
import os
import json
import re
from pymongo import MongoClient
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("WEATHER_COLLECTION_NAME")


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_region(lat, lon):
    """
    Determine the region in the USA based on latitude and longitude.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        str: Name of the region (e.g., "Northeast", "Southwest", etc.).
    """
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

def load_weather_data(input_dir):
    """
    Load weather data from JSON files and parse hourly information.

    Args:
        input_dir (str): Directory containing raw weather data files.

    Returns:
        list[dict]: A list of parsed weather data dictionaries.
    """
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
            logging.error(f"Error decoding JSON in file {file}: {e}")
        except KeyError as e:
            logging.error(f"Missing key in file {file}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error processing file {file}: {e}")

    return all_data

def summarize_data(data):
    """
    Generate daily summaries of weather data.

    Args:
        data (list[dict]): List of parsed weather data.

    Returns:
        pd.DataFrame: A DataFrame containing daily summaries.
    """
    df = pd.DataFrame(data)

    if df.empty:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["day"] = pd.to_datetime(df["timestamp"].dt.date)
    df["region"] = df.apply(lambda row: get_region(row["latitude"], row["longitude"]), axis=1)

    daily_summary = df.groupby(["region", "day"]).agg({
        "temperature": "mean",
        "wind_speed": "max"
    }).reset_index()

    daily_summary["summary_date"] = datetime.now().isoformat()
    return daily_summary

def save_to_mongo(data, uri, db_name, collection_name):
    """
    Save summarized data to a MongoDB collection.

    Args:
        data (pd.DataFrame): DataFrame containing summarized weather data.
        uri (str): MongoDB URI.
        db_name (str): MongoDB database name.
        collection_name (str): MongoDB collection name.
    """
    try:
        client = MongoClient(uri)
        db = client[db_name]
        collection = db[collection_name]

        documents = data.to_dict(orient="records")
        if documents:
            collection.insert_many(documents)
            logging.info(f"Inserted {len(documents)} summaries into MongoDB.")
        client.close()
    except Exception as e:
        logging.error(f"Failed to save data to MongoDB: {e}")

def cleanup_files(files):
    """
    Delete processed files.

    Args:
        files (list[str]): List of file paths to delete.
    """
    for file in files:
        try:
            os.remove(file)
            logging.info(f"Deleted file: {file}")
        except OSError as e:
            logging.error(f"Error deleting file {file}: {e}")

if __name__ == "__main__":
    """
    Main script to load, process, and save weather data.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    input_dir = os.path.join(script_dir, "../data/raw/weather")

    files = glob.glob(os.path.join(input_dir, "*.json"))

    all_data = load_weather_data(input_dir)

    if all_data:
        daily_summary = summarize_data(all_data)

        if not daily_summary.empty:
            save_to_mongo(daily_summary, MONGO_URI, DB_NAME, COLLECTION_NAME)
        else:
            logging.warning("No valid data to save.")
    else:
        logging.warning("No valid data to process.")

    cleanup_files(files)
