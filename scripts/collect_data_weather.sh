#!/bin/bash


timestamp=$(date +"%Y%m%d_%H%M%S")


script_dir=$(dirname "$(realpath "$0")")


project_dir=$(realpath "$script_dir/..")


directory="$project_dir/data/raw/weather"
mkdir -p "$directory"

#  geographic bounds for the data collection  : USA
latitude_start=24
latitude_end=49
longitude_start=-125
longitude_end=-66

# Interval for the grid points
interval=5


log_file="$project_dir/logs/weather_data_download_$timestamp.log"


download_weather_data() {
    local lat=$1
    local lon=$2
    local output_file="$directory/weather_data_${lat}_${lon}_$timestamp.json"
    local url="https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&hourly=temperature_2m,wind_speed_10m,cloudcover&forecast_days=1&past_days=61"

    
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
