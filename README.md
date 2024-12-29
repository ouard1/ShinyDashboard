

---

# 📊 Real-Time Dashboard for Crude Oil Analysis

**Authors**: Ouarda Boumansour & Melissa Merabet  
**Date**: December 29, 2024  

---

## 🌟 Overview

This project implements a **real-time dashboard** that integrates and analyzes various datasets related to crude oil prices, forex exchange rates, and weather data. The dashboard allows users to interactively explore trends, correlations, and key insights through visualizations.

### Key Features
- **Crude Oil Price Analysis**: Visualize crude oil prices over time, including distributions and price fluctuations.
- **Forex Data Visualization**: Display the most recent forex exchange rates and their impact on crude oil prices.
- **Weather Data Integration**: Correlate weather variables like temperature and wind speed with crude oil price trends.
- **Correlation Analysis**: Examine the relationship between crude oil prices and forex exchange rates using heatmaps and scatter plots.

The data is fetched from multiple APIs and stored in **MongoDB collections**. The dashboard is built using **Shiny (Python)** for interactive visualizations powered by **Plotly**.

---

## 🌐 Data Sources

1. **Open-Meteo API**:  
   Supplies real-time weather data, including temperature and wind speed, used to analyze the impact of extreme weather on energy demand.

2. **Alpha Vantage API (Forex Rates)**:  
   Offers real-time forex rates for various currencies (USD, CAD, NOK, RUB, SAR).

3. **Alpha Vantage API (Crude Oil Data)**:  
   Supplies daily crude oil price data.

---

## 🔧 Features

- **Interactive UI**: Select different years, months, regions, and weather variables to dynamically filter and display the data.
- **Crude Oil Price Trends**: A line plot and box plot to analyze crude oil price trends over time.
- **Forex Data Cards**: Display real-time forex exchange rates for selected currencies.
- **Weather vs. Crude Oil Prices**: A scatter plot showing the relationship between weather variables and crude oil prices.
- **Correlation Heatmap**: A heatmap that visualizes correlations between forex exchange rates and crude oil prices.

---

## 📋 Requirements

- **Python 3.x**
- **Pandas**
- **Plotly**
- **Shiny (Python)**
- **MongoDB**
- **APIs for data sources (Open-Meteo, Alpha Vantage)**

---

## ⚙️ Setup Instructions

### Clone the Repository
Clone the project repository:
```bash
git clone https://github.com/ouard1/ShinyDashboard.git
cd ShinyDashboard
```

### Install Python Dependencies
Ensure you have Python 3.x installed. Then, install the required libraries:
```bash
pip install -r requirements.txt
```

### Set Up MongoDB
- Set up a local or remote MongoDB instance.
- Populate the MongoDB collections (`crude_oil_data`, `forex_data`, `weather_data`, etc.) with data from the relevant APIs.

### Run the Shiny App
To launch the dashboard, use the following command:
```bash
python app.py
```
This will start the Shiny server, and you can access the dashboard in your browser at `http://localhost:5000`.

---

## 🗂️ File Structure

The project directory has the following structure:

```plaintext
real-time-dashboard-crude-oil
├── data/                # Directory for raw and processed data
│   ├── raw/             # Raw data files
│       ├── weather_data/
│       ├── forex_data/
│       ├── crude_oil_data/
├── logs/                # Directory for logs
├── scripts/             # Scripts for data collection and analysis
│   ├── weather_data_collector.sh
│   ├── crude_oil_data_collector.sh 
│   ├── forex_data_collector.sh    
│   ├── weather_data_summarize.py
│   ├── forex_data_summarize.py
│   ├── crude_oil_data_summarize.py       
│        
├── dashboard/           # Shiny app files
│   ├── app.py           # Shiny app server logic and UI
│   ├── server.py        # Shiny app server logic
│   ├── ui.py            # Shiny app UI
├── report/              # Documentation and project report
│   └── report.md        # Project report file
├── cronjobs/            # Cron job configurations for automating data updates
│   └── crontab.txt      # Cron job file for updating data from APIs
└── requirements.txt     # Python dependencies for the project
```

---

## 🛠️ Usage

- **Year and Month Selection**: Use the dropdown to select a specific year or month for filtering the crude oil price data.
- **Region Selection**: Choose a region from the dropdown to view data relevant to that region.
- **Weather Variables**: Select either temperature or wind speed to see how they correlate with crude oil prices.
- **Forex Exchange Rate**: View the most recent exchange rates for different currencies and their impact on crude oil prices.

---

