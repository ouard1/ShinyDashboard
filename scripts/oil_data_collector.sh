#!/bin/bash

#Répertoire pour stocker les fichiers
DATA_DIR="$HOME/brent_data"
API_URL="https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=IAXISE01Z7646DIA"

# Répertoire partagé VirtualBox
SHARED_DIR="/mnt/shared"

#Créer les répertoires si inexistants
mkdir -p "$DATA_DIR"
mkdir -p "$SHARED_DIR"

#Obtenir la date et l'heure actuelles formatées
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

#Nom du fichier 
OUTPUT_FILE="$DATA_DIR/brent_data_$TIMESTAMP.json"

#Télécharger les données de l'API et les stocker dans le fichier
curl -s "$API_URL" -o "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] Données téléchargées avec succès : $OUTPUT_FILE"
    # Copier le fichier JSON dans le dossier partagé
    cp "$OUTPUT_FILE" "$SHARED_DIR"
    echo "[$(date)] Fichier copié dans le dossier partagé."

else
    echo "[$(date)] Erreur lors du téléchargement des données." >&2
    rm -f "$OUTPUT_FILE"  # Supprimer le fichier en cas d'erreur
fi
