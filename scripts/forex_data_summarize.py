import os 
import json
from pymongo import MongoClient 

# Répertoire où sont stockés les fichiers json
DATA_DIR="../data/raw/forex_data"

mongo_uri = "mongodb://localhost:27017"
client = MongoClient(mongo_uri)

forex_db = client["dashboard_app_db"]
forex_collection = forex_db["forex_rates"]

# Fonction pour insérer ou remplacer les données
def upsert_exchange_rates(collection, data):
    for record in data:
        collection.replace_one(
            {"device": record["device"]},  
            record,  
            upsert=True  
        )

def process_file(file_path):
    with open(file_path, "r") as f:
        try:
            file_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de lecture du fichier JSON : {file_path}")

    extracted_data = []
    for currency, details in file_data.items():
        exchange_info = details["Realtime Currency Exchange Rate"]
        device = exchange_info["3. To_Currency Code"]
        exchange_rate = exchange_info["5. Exchange Rate"]
        last_refreshed = exchange_info["6. Last Refreshed"]

        extracted_data.append({
            "device": device,
            "exchange_rate": exchange_rate,
            "last_refreshed": last_refreshed
        })
    
    upsert_exchange_rates(forex_collection, extracted_data)
    


for file_name in os.listdir(DATA_DIR):
    if file_name.endswith(".json"):
        file_path = os.path.join(DATA_DIR, file_name)
        process_file(file_path)

        os.remove(file_path)
        print(f"fichier supprimé : {file_name}")