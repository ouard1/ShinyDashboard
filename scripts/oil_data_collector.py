import os
import json
from pymongo import MongoClient
from datetime import datetime

# Répertoire où les fichiers JSON sont stockés (le dossier partagé)
DATA_DIR = "C:/Users/melissa.merabet/Desktop/oil_data_linux"


client = MongoClient("mongodb://localhost:27017/") 
db = client["testLinuxDataBase"]  
collection = db["oilDataCollection"]  


#Fonction pour vérifier si une donnée existe déjà dans MongoDB
def data_exists(date, value):
    return collection.find_one({"date": date, "value": value}) is not None


# Récupérer les données depuis l'API
def process_file(file_path):
    with open(file_path, "r") as f:
        try: 
            file_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de lecture du fichier JSON : {file_path}")
            return
    new_records = []
    for record in file_path['data']:
        date = record.get("date")
        value = record.get("value")
        if date and value and not data_exists(date, value):
            new_records.append({"date": date, "value": float(value)})

    if new_records:
        collection.insert_many(new_records)
        print(f"Inséré {len(new_records)} nouvelles données depuis {file_path}")
    else:
        print(f"Aucune nouvelle donnée à insérer depuis {file_path}")


# Parcourir les fichiers JSON dans le répertoire
for file_name in os.listdir(DATA_DIR):
    if file_name.endswith(".json"):
        file_path = os.path.join(DATA_DIR, file_name)
        process_file(file_path)

        os.remove(file_path)
        print(f" fichier supprimé : {file_name}")

   