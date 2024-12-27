import os 
import json
from pymongo import MongoClient 

# Répertoire où sont stockés les fichiers json
DATA_DIR="../data/raw/crude_oil"

mongo_uri = "mongodb://localhost:27017"
client = MongoClient(mongo_uri)

crude_oil_db = client["dashboard_app_db"]
collection_db = crude_oil_db["crude_oil_prices"]


def data_exists(date, value):
    return collection_db.find_one({"date": date, "value": value}) is not None

def process_file(file_path):
    with open(file_path, "r") as f:
        try:
            file_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de lecture du fichier JSON : {file_path}")

    new_records = []
    for record in file_data['data']:
        date = record.get("date")
        value = record.get("value")
        if date and value and not data_exists(date, value):
            new_records.append({"date": date, "value": value})
    
    if new_records:
        collection_db.insert_many(new_records)
        print(f"Inséré {len(new_records)} nouvells données depuis {file_path}")
    else:
        print(f"Aucune nouvelle donnée à insérer depuis {file_path}")


for file_name in os.listdir(DATA_DIR):
    if file_name.endswith(".json"):
        file_path = os.path.join(DATA_DIR, file_name)
        process_file(file_path)

        os.remove(file_path)
        print(f"fichier supprimé : {file_name}")
   