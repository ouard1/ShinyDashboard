#!/bin/bash

# --------------------------------------------------------------------------------------
# Script Name: Weather Data Downloader
# Description: 
#   This script downloads weather data for specific geographic coordinates in the USA 
#   using the Open-Meteo API. The data includes temperature, wind speed, and cloud cover 
#    The script saves the data in JSON files and compresses old files.
# 
# Features:
#   - Downloads weather data for latitude and longitude ranges with a defined interval.
#   - Saves the data to timestamped JSON files in a specific directory.
#   - Logs successes and failures to a log file.
#   
# 
# Inputs:
#   - Latitude range: 24 to 49 (inclusive)
#   - Longitude range: -125 to -66 (inclusive)
#   - Interval: 2 degrees
# 
# Outputs:
#   - JSON files stored in the "data/raw/weather" directory.
#   - Log file recording the download process.
# 
# Requirements:
#   - curl: for API requests
#   - gzip: for file compression
# 
# Usage:
#   Run the script directly in a Bash shell. No additional arguments are required.
# --------------------------------------------------------------------------------------

timestamp=$(date +"%Y%m%d_%H%M%S")
script_dir=$(dirname "$(realpath "$0")")
project_dir=$(realpath "$script_dir/..")


directory="$project_dir/data/raw/weather"
mkdir -p "$directory"


latitude_start=24
latitude_end=49
longitude_start=-125
longitude_end=-66


interval=2


log_file="$project_dir/logs/weather_data_download_$timestamp.log"


download_weather_data() {
    local lat=$1
    local lon=$2
    local output_file="$directory/weather_data_${lat}_${lon}_$timestamp.json"
    local url="https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&hourly=temperature_2m,wind_speed_10m,cloudcover&forecast_days=1"

    
    curl -s --retry 3 --retry-delay 2 "$url" -o "$output_file"

    
    if [ -s "$output_file" ]; then
        echo "[$(date)] Data for $lat, $lon successfully saved to $output_file" >> "$log_file"
    else
        echo "[$(date)] Failed to download data for $lat, $lon" >> "$log_file"
      
        rm -f "$output_file"
    fi
}


for ((lat = latitude_start; lat <= latitude_end; lat += interval)); do
    for ((lon = longitude_start; lon <= longitude_end; lon += interval)); do
        download_weather_data "$lat" "$lon"
    done
done


find "$directory" -type f -name "*.json" -mtime +7 -exec gzip {} \;
echo "[$(date)] Old files compressed successfully" >> "$log_file"
