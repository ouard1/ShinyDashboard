import os 
import json
from pymongo import MongoClient 
from dotenv import load_dotenv


script_dir = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(script_dir, "../data/raw/crude_oil")

# Load environment variables from the .env file
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name =  os.getenv("DB_NAME")
collection_name = os.getenv("FOREX_COLLECTION_NAME")



client = MongoClient(mongo_uri)
forex_db = client[db_name]
forex_collection = forex_db[collection_name]

# Fonction pour insérer ou remplacer les données
def upsert_exchange_rates(collection, data):
    """
    Insert or update exchange rate data in the MongoDB collection.

    Args:
        collection (MongoClient collection): The MongoDB collection where the data will be inserted.
        data (list of dict): A list of dictionaries containing exchange rate data to be upserted.
    """
    for record in data:
        collection.replace_one(
            {"device": record["device"]},  
            record,  
            upsert=True  
        )

def process_file(file_path):
    """
    Process a single JSON file, extract relevant exchange rate data, and upsert it to MongoDB.

    Args:
        file_path (str): Path to the JSON file to be processed.

    Returns:
        None
    """
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