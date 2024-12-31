#!/bin/bash


################################################################################
# Script: download_forex_data.sh
# Description: Downloads forex data for specified currencies (USD to SAR, EUR, etc.) 
#              from the Alpha Vantage API and saves the response in a JSON file.
#
# Usage:
# 1. Place script and .env file in the project directory.
# 2. Run the script: ./download_forex_data.sh
#
# Requirements:
# - .env file containing API_KEY.
# - curl and sed installed.
#
# Output:
# - Saves forex data as a JSON file in data/raw/forex_data/ with a timestamp.
################################################################################

export $(grep -v '^#' .env | xargs)

API_KEY="IAXISE01Z7646DIA"
BASE_URL="https://www.alphavantage.co/query"
DEVICES=("SAR" "EUR" "CNY" "CAD" "NGN")




TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

script_dir=$(dirname "$(realpath "$0")")
project_dir=$(realpath "$script_dir/..")
directory="$project_dir/data/raw/forex_data"


mkdir -p "$directory"

OUTPUT_FILE="$directory/forex_data_$TIMESTAMP.json"



echo "{" > "$OUTPUT_FILE"

for DEVICE in "${DEVICES[@]}"; do
    API_URL="${BASE_URL}?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=${DEVICE}&apikey=${API_KEY}"
    RESPONSE=$(curl -s "$API_URL")

    if [ $? -eq 0 ]; then 
        echo "\"$DEVICE\": $RESPONSE," >> "$OUTPUT_FILE"
        echo "[$(date)] Données téléchargées avec succès : $DEVICE"
    else 
        echo "[$(date)] Erreur lors du téléchargement des données pour $DEVICE." >&2
        rm -f "$OUTPUT_FILE"
    fi
done 

sed -i '$ s/,$//' "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo "Données consolidées enregitrées dans : $OUTPUT_FILE"