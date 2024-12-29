#!/bin/bash

#----------------------------------------------------------------------------------------------------
# Script to download daily crude oil data (WTI) from the Alpha Vantage API
# and save it to a timestamped JSON file in the `data/raw/crude_oil` directory.
# The API key is stored in a .env file for security.

# Requirements: curl, .env file with API_KEY and API_URL

# Usage:
# 1. Set the API_KEY and API_URL in a .env file.
# 2. Run the script to fetch and store the data.
#-----------------------------------------------------------------------------------------------------


TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

script_dir=$(dirname "$(realpath "$0")")
project_dir=$(realpath "$script_dir/..")
directory="$project_dir/data/raw/crude_oil"

export $(grep -v '^#' "$script_dir/.env" | xargs)


API_URL="${API_URL}&apikey=${API_KEY}"


mkdir -p "$directory"

OUTPUT_FILE="$directory/crude_oil_data_$TIMESTAMP.json"

curl -s "$API_URL" -o "$OUTPUT_FILE"

if [ $? -eq 0 ]; then 
    echo "[$(date)] Données téléchargées avec succès : $OUTPUT_FILE"
else 
    echo "[$(date)] Erreur lors du téléchargement des données." >&2
    rm -f "$OUTPUT_FILE"
fi