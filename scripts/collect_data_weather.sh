#!/bin/bash

timestamp=$(date +"%Y%m%d_%H%M%S")

directory="/home/ouarda/dashboard/ShinyDashboard/data/raw/weather"
mkdir -p "$directory"


latitude_start=24
latitude_end=49
longitude_start=-125
longitude_end=-66


interval=1


for ((lat = latitude_start; lat <= latitude_end; lat += interval)); do
    for ((lon = longitude_start; lon <= longitude_end; lon += interval)); do
        
        
        url="https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&hourly=temperature_2m,wind_speed_10m,cloudcover&timezone=America/New_York"
        
        
        output_file="$directory/weather_data_${lat}_${lon}_$timestamp.json"
        curl -s "$url" -o "$output_file"
        
        echo "Data for $lat, $lon saved to $output_file"
    done
done
