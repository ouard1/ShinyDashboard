import os 
import json
from pymongo import MongoClient 
from dotenv import load_dotenv
import pandas as pd

script_dir = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(script_dir, "../data/raw/crude_oil")

# Load environment variables from the .env file
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name =  os.getenv("DB_NAME")
collection_name = os.getenv("CRUDE_COLLECTION_NAME")

if not mongo_uri or not db_name or not collection_name:
    raise ValueError("Une ou plusieurs variables d'environnement sont manquantes.")



client = MongoClient(mongo_uri)
crude_oil_db = client[db_name]
crude_oil_collection = crude_oil_db[collection_name]

def data_exists(date, value):
    """Vérifie si les données existent déjà dans la base MongoDB en fonction de la date et de la valeur."""
    return crude_oil_collection.find_one({"date": date, "value": value}) is not None

    
def preprocess_dataframe(df):
    """Prétraite les données : convertir la date et la valeur, et supprime les prifs négatifs"""
    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    # Supprimer les lignes où la colonne 'value' est négative
    df = df[df['value'] >= 0]
    return df

def create_missing_dates(df):
    """Crée les dates manquantes pour combler l'intervalle entre les dates."""
    full_date_range = pd.date_range(start=df["date"].min(), end=pd.to_datetime('today'), freq='D')
    missing_dates = full_date_range.difference(df["date"])
    missing_df = pd.DataFrame(missing_dates, columns=["date"])
    missing_df['value'] = None  
    missing_df["year"] = missing_df["date"].dt.year
    missing_df["month"] = missing_df["date"].dt.month
    return missing_df

def combine_and_sort_data(df, missing_df):
    """Combine les données existantes avec les dates manquantes et les trie."""
    df = df.dropna(how="all", axis=1)
    missing_df = missing_df.dropna(how="all", axis=1)
    combined_df = pd.concat([df, missing_df], ignore_index=True)
    combined_df = combined_df.sort_values(by="date")
    combined_df["_id"] = range(1, len(combined_df) + 1)
    return combined_df

def interpolate_missing_values(df):
    """Interpole les valeurs manquantes dans le DataFrame."""
    df['value'] = df['value'].interpolate()
    return df

def process_file(file_path):
    """Traite un fichier JSON, le prétraite et retourne un DataFrame."""
    with open(file_path, "r") as f:
        try:
            file_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de lecture du fichier JSON : {file_path}")
    df = pd.DataFrame(file_data['data'])
    df = preprocess_dataframe(df)
    missing_df = create_missing_dates(df)
    df = combine_and_sort_data(df, missing_df)
    df = interpolate_missing_values(df)
    return df

def load_and_process_crude_oil_data():
    """Charge et traite les données, puis les stocke dans MongoDB."""
    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".json"):
            file_path = os.path.join(DATA_DIR, file_name)
            df = process_file(file_path)
            
            if df is not None:
                new_records = []
                for _, row in df.iterrows():
                    date = row["date"]
                    value = row["value"]
                    if not data_exists(date, value):  
                        new_records.append(row.to_dict())

                if new_records:
                    try:
                        crude_oil_collection.insert_many(new_records)
                        print(f"Inséré {len(new_records)} nouvelles données depuis {file_path}")
                    except Exception as e:
                        print(f"Erreur lors de l'insertion dans MongoDB : {e}")
                else:
                    print(f"Aucune nouvelle donnée à insérer depuis {file_path}")
                
            
                try:
                    os.remove(file_path)
                    print(f"Fichier supprimé : {file_name}")
                except Exception as e:
                    print(f"Erreur lors de la suppression du fichier {file_name}: {e}")


load_and_process_crude_oil_data()


