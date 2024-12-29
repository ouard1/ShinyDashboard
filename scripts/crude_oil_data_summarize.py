import os 
import json
from pymongo import MongoClient 

# Répertoire où sont stockés les fichiers json
DATA_DIR="../data/raw/crude_oil"

mongo_uri = "mongodb://localhost:27017"
client = MongoClient(mongo_uri)

crude_oil_db = client["dashboard_app_db"]
crude_oil_collection = crude_oil_db["crude_oil_prices"]

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
            new_records = []
            for _, row in df.iterrows():
                date = row["date"]
                value = row["value"]
                if not data_exists(date, value):  
                    new_records.append(row.to_dict())
            if new_records:
                crude_oil_collection.insert_many(new_records)
                print(f"Inséré {len(new_records)} nouvelles données depuis {file_path}")
            else:
                print(f"Aucune nouvelle donnée à insérer depuis {file_path}")
            os.remove(file_path)
            print(f"Fichier supprimé : {file_name}")


load_and_process_crude_oil_data()


