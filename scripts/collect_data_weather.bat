@echo off
setlocal enabledelayedexpansion

:: Get current date and time for the filename
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value"') do set datetime=%%I
set year=!datetime:~0,4!
set month=!datetime:~4,2!
set day=!datetime:~6,2!
set hour=!datetime:~8,2!
set minute=!datetime:~10,2!
set second=!datetime:~12,2!
set timestamp=!year!-!month!-!day!_!hour!-!minute!-!second!

:: Define the output directory and create it if it doesn't exist
set directory=weather_data
if not exist "!directory!" mkdir "!directory!"

:: Define the grid bounds for the USA
set latitude_start=24
set latitude_end=49
set longitude_start=-125
set longitude_end=-66

:: Define the interval for grid (e.g., 1 degree)
set interval=1

:: Loop through the latitudes and longitudes and fetch data for each
for /L %%lat in (%latitude_start%, %interval%, %latitude_end%) do (
    for /L %%lon in (%longitude_start%, %interval%, %longitude_end%) do (
        
        :: Construct the API URL for each latitude and longitude
        set "url=https://api.open-meteo.com/v1/forecast?latitude=%%lat&longitude=%%lon&hourly=temperature_2m,wind_speed_10m,cloudcover&timezone=America/New_York"
        
        :: Use curl to fetch the data and save it to a JSON file
        curl -s !url! > "!directory!\weather_data_%%lat_%%lon_!timestamp!.json"
        
        echo Data for %%lat,%%lon saved to !directory!\weather_data_%%lat_%%lon_!timestamp!.json
    )
)

endlocal
