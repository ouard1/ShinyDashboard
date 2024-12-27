#!/bin/bash



API_URL="https://www.alphavantage.co/query?function=BRENT&interval=daily&apikey=IAXISE01Z7646DIA"



TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

script_dir=$(dirname "$(realpath "$0")")
project_dir=$(realpath "$script_dir/..")
directory="$project_dir/data/raw/crude_oil"


mkdir -p "$directory"

OUTPUT_FILE="$directory/crude_oil_data_$TIMESTAMP.json"

curl -s "$API_URL" -o "$OUTPUT_FILE"

if [ $? -eq 0 ]; then 
    echo "[$(date)] Données téléchargées avec succès : $OUTPUT_FILE"
else 
    echo "[$(date)] Erreur lors du téléchargement des données." >&2
    rm -f "$OUTPUT_FILE"
fi