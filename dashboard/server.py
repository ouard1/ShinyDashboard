from shiny import render, reactive, ui
import pandas as pd
import plotly.express as px
from datetime import datetime
from pymongo import MongoClient
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import numpy as np
from dotenv import load_dotenv
import os
import sys

# Load environment variables from the scripts/.env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', '.env')
load_dotenv(dotenv_path)

mongo_uri = os.getenv("MONGO_URI")
db_name =  os.getenv("DB_NAME")
crude_oil = os.getenv("CRUDE_COLLECTION_NAME")
weather = os.getenv("WEATHER_COLLECTION_NAME")
forex = os.getenv("FOREX_COLLECTION_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]

collection_crude_oil = db[crude_oil ]
collection_forex = db[forex]
collection_weather = db[weather]

def load_crude_oil_data(collection):
    """
    Load crude oil price data from the specified MongoDB collection.
    - Converts the 'date' column to datetime and extracts the 'year' and 'month' columns.
    - Returns a DataFrame containing the crude oil price data.
    """
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year  
    df["month"] = df["date"].dt.month
    return df

def load_recent_forex_data(collection):
    """
    Load the most recent Forex data for the given devices.
    """
    recent_data = []
    devices = ["SAR", "EUR", "CNY", "CAD", "NGN"]
    for device in devices:
        data = collection.find({"device": device}).sort("last_refreshed", -1).limit(1)
        recent_data.extend(list(data))

    if not recent_data:
        raise ValueError("No recent Forex data found for the specified devices.")

    df = pd.DataFrame(recent_data)
    df['last_refreshed'] = pd.to_datetime(df['last_refreshed'])
    return df


def load_full_forex_data(collection):
    """
    Load the full Forex data for correlation analysis.
    """
    data = list(collection.find())
    if not data:
        raise ValueError("No Forex data found in the collection.")

    df = pd.DataFrame(data)
    df['last_refreshed'] = pd.to_datetime(df['last_refreshed'])
    return df

    
    

def load_weather_data(collection):
    """
    Load weather data from the specified MongoDB collection.
    - Converts 'day' column to datetime, 'temperature' and 'wind_speed' columns to numeric.
    - Raises an exception if the 'day' column is missing or the collection is empty.
    """
    data = list(collection.find())
    if not data:
        raise ValueError("La collection MongoDB 'weather' est vide ou n'a pas de données.")
    df = pd.DataFrame(data)
    
    if "day" not in df.columns:
        raise KeyError("La colonne 'day' est absente. Vérifiez les données MongoDB ou leur extraction.")
    df["date"] = pd.to_datetime(df["day"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["wind_speed"] = pd.to_numeric(df["wind_speed"], errors="coerce")
    return df

df_crude_oil = load_crude_oil_data(collection_crude_oil)
df_recent_forex = load_recent_forex_data(collection_forex)
df_forex = load_full_forex_data(collection_forex)
df_weather = load_weather_data(collection_weather)
df_combined = pd.merge(df_crude_oil, df_weather, on="date", how="inner")

def server(input, output, session):
    """
    Define the server logic for the Shiny app.
    - Includes rendering UI elements such as dropdowns for selecting year, month, region, and weather variable.
    - Generates plots such as line plots, box plots, scatter plots, and correlation heatmaps.
    """
    unique_years = sorted(df_crude_oil["year"].unique())
    unique_months = range(1, 13)
    unique_regions = sorted(df_combined["region"].unique())
    weather_variables = ["temperature", "wind_speed"]

    @output
    @render.ui
    def year_selected(): 
        choices = ["All years"] + [str(year) for year in unique_years]
        return ui.div(
            ui.input_select(
                id="selected_year",
                label="Select a year",
                choices=choices,
                selected="All years"
            ), 
            style="margin-left: 20px;"
        )
    
    @output
    @render.ui
    def month_selected(): 
        choices = ["All months"] + [str(month) for month in unique_months]
        return ui.div(
            ui.input_select(
                id="selected_month",
                label="Select a month",
                choices=choices,
                selected="All months"
            ), 
            style="margin-left: 20px;"
        )

    @output
    @render.ui
    def price_plot():
        global df_crude_oil
        df = df_crude_oil.copy()

        year = input.selected_year() if input.selected_year() else "All years"
        month = input.selected_month() if input.selected_month() else "All months"
        filtered_df = df.copy()

        if year != "All years":
            filtered_df = filtered_df[filtered_df["year"] == int(year)]

        if month != "All months":
            filtered_df = filtered_df[filtered_df["month"] == int(month)]
        
        fig_line = px.line(
            filtered_df,
            x=filtered_df["date"],
            y=filtered_df["value"],
            title="Crude Oil Prices Over Time",
            labels={"date": "Date", "value": "Price (USD)"},
            template="plotly_white",
        )
        fig_line.update_traces(line=dict(color="#6a1636", width=2))
        fig_line.update_layout(
            title_font_size=20,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=40),
        )
        # Box plot for value distribution
        fig_box = px.box(
            filtered_df,
            y="value",
            title="Price Distribution",
            labels={"value": "Price (USD)"},
            template="plotly_white",
        )

        fig_box.update_traces(marker_color="#6a1636", boxmean=True)
        fig_box.update_layout(
            title_font_size=20,
            yaxis_title="Price (USD)",
            margin=dict(l=40, r=40, t=60, b=40),
        )
        
        #return ui.HTML(fig_line.to_html(full_html=False))
        return ui.HTML(f"""
            <div style="display: flex; flex-direction: row; gap: 40px;  background-color: white ;padding: 10px;justify-content: space-between;">
                <div style= " background-color: #f9f9f9;padding: 20px;border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); width: 1000px">
                    {ui.HTML(fig_line.to_html(full_html=False))}
                </div>
                 <div style= " background-color: #f9f9f9;padding: 20px;border-radius: 10px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); ">
                    {ui.HTML(fig_box.to_html(full_html=False))}
                </div>
            </div>
        """)


    @output
    @render.ui
    def card_forex():
        """
        Render Forex cards showing the most recent data for each device.
        """
        currency_data = df_recent_forex[['device', 'exchange_rate', 'last_refreshed']].to_dict(orient='records')

        if not currency_data:
            return ui.div(
                "No Forex data available.",
                style="text-align: center; font-size: 18px; margin-top: 20px;"
            )

        cards = []
        for item in currency_data:
            formatted_date = item['last_refreshed'].strftime("%d-%m-%Y %H:%M") if item['last_refreshed'] else "N/A"
            cards.append(
                ui.card(
                    ui.card_header(
                        item['device'],
                        style="text-align: center; font-weight: bold; background-color: #6a1636; color: white;"
                    ),
                    ui.div(
                        f"Exchange Rate: {item['exchange_rate']}",
                        style="text-align: center; font-size: 16px; margin: 10px;"
                    ),
                    ui.div(
                        f"Last Updated: {formatted_date}",
                        style="text-align: center; font-size: 12px; color: gray; margin-top: 5px;"
                    ),
                    style="flex: 1; margin: 10px; min-width: 150px;"
                )
            )

        return ui.div(
            *cards,
            style="display: flex; flex-wrap: wrap; justify-content: space-around; margin-bottom: 20px;"
        )


    @output
    @render.ui
    def region_selector():
        return ui.input_select(
            id="selected_region",
            label="Select Region",
            choices=["All regions"] + unique_regions,
            selected="All regions"
        )

    @output
    @render.ui
    def variable_selector():
        return ui.input_select(
            id="selected_variable",
            label="Select Weather Variable",
            choices=weather_variables,
            selected="temperature"
        )

    @output
    @render.ui
    def correlation_plot():
        selected_region = input.selected_region() if input.selected_region() else "All regions"
        selected_variable = input.selected_variable()

        df_filtered = df_combined.copy()

        if selected_region != "All regions":
            df_filtered = df_filtered[df_filtered["region"] == selected_region]

        
        correlation = df_filtered[selected_variable].corr(df_filtered["value"])

        
        scatter_fig = px.scatter(
            df_filtered,
            x=selected_variable,
            y="value",
            title=f"Correlation between {selected_variable} and Crude Oil Prices (Corr: {correlation:.2f})",
            labels={selected_variable: selected_variable.capitalize(), "value": "Crude Oil Price (USD)"},
            template="plotly_white"
        )
        scatter_fig.update_traces(marker=dict(color='rgb(128, 0, 32)', size=8))
        scatter_fig.update_layout(
            title_font_size=20,
            margin=dict(l=40, r=40, t=60, b=40),
        )

        return ui.HTML(scatter_fig.to_html(full_html=False))
  


    def calculate_forex_crude_correlation(df_crude_oil, df_forex):
        
        df_forex_copy = df_forex.rename(columns={'last_refreshed': 'date'})
        
        df_crude_oil['date'] = pd.to_datetime(df_crude_oil['date']).dt.date
        df_forex_copy['date'] = pd.to_datetime(df_forex_copy['date']).dt.date

       
        df_combined = pd.merge(df_crude_oil, df_forex_copy, on="date", how="inner")

       
        df_combined['value'] = pd.to_numeric(df_combined['value'], errors='coerce')
        df_combined['exchange_rate'] = pd.to_numeric(df_combined['exchange_rate'], errors='coerce')

        
        forex_columns = ['exchange_rate']
        df_corr = df_combined[['device', 'value'] + forex_columns]

       
        correlation_results = {}
        for device in df_corr['device'].unique():
            df_device = df_corr[df_corr['device'] == device]
            if not df_device.empty:
                
                correlation = df_device[['value', 'exchange_rate']].corr().iloc[0, 1]
                correlation_results[device] = correlation

        
        correlation_matrix = pd.DataFrame.from_dict(
            correlation_results, orient='index', columns=['Correlation']
        )
        correlation_matrix.index.name = 'Device'
        
        return correlation_matrix


    @output
    @render.ui
    def correlation_heatmap():
      
        correlation_matrix = calculate_forex_crude_correlation(df_crude_oil, df_forex)
        custom_colorscale = [
        [0, '#2e081b'],      
        [0.25, '#4d1028'],  
        [0.5, '#6a1636'],    
        [0.75, '#a34274'],  
        [1, '#e1b3c3']      
         ]
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=correlation_matrix['Correlation'].values.reshape(-1, 1), 
            x=['Correlation'],  
            y=correlation_matrix.index, 
            colorscale=custom_colorscale,
            zmin=-1, zmax=1,
            colorbar=dict(title="Correlation Coefficient")
        ))

        
        fig_heatmap.update_layout(
            title="Correlation Heatmap: Crude Oil Prices vs Forex Exchange Rates",
            xaxis_title="Exchange Rates",
            yaxis_title="Currency",
            template="plotly_white",
            title_font_size=20,
            margin=dict(l=40, r=40, t=60, b=40),
        )

        return ui.HTML(fig_heatmap.to_html(full_html=False))
