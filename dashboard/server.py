from shiny import render, reactive, ui
import pandas as pd
import plotly.express as px
from datetime import datetime
from pymongo import MongoClient
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import numpy as np

client = MongoClient("mongodb://localhost:27017/")
db = client["dashboard_app_db"]
collection_crude_oil = db["crude_oil_prices"]
collection_forex = db["forex_rates"]
collection_weather = db["weather"]

def load_crude_oil_data(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df


def load_forex_data(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df

def load_weather_data(collection):
    data = list(collection.find())
   
   
    if not data:
        raise ValueError("La collection MongoDB 'weather' est vide ou n'a pas de données.")

  
    df = pd.DataFrame(data)
   
    print("Colonnes dans le DataFrame extrait :", df.columns)

    
    if "day" not in df.columns:
        raise KeyError("La colonne 'day' est absente. Vérifiez les données MongoDB ou leur extraction.")


    df["date"] = pd.to_datetime(df["day"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["wind_speed"] = pd.to_numeric(df["wind_speed"], errors="coerce")
    return df   

df_crude_oil = load_crude_oil_data(collection_crude_oil)
df_forex = load_forex_data(collection_forex)
df_weather = load_weather_data(collection_weather)
df_combined = pd.merge(df_crude_oil, df_weather, on="date", how="inner")

def server(input, output, session):
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
            <div style="display: flex; flex-direction: row; gap: 40px;">
                <div>
                    {ui.HTML(fig_line.to_html(full_html=False))}
                </div>
                <div>
                    {ui.HTML(fig_box.to_html(full_html=False))}
                </div>
            </div>
        """)


    @output
    @render.ui
    def card_forex():
        global df_forex
        currency_data = df_forex[['device', 'exchange_rate', 'last_refreshed']].to_dict(orient='records')
        card_content = ""
        card_content = "".join([
            f"""
            <div style="margin-bottom: 10px; text-align: center; font-size: 18px;">
                <strong>{item['device']}:</strong> {item['exchange_rate']} <br>
            </div>
            """
            for item in currency_data
        ])
        original_date = currency_data[0]['last_refreshed'] if currency_data else "N/A"
        formatted_date = (
            datetime.strptime(original_date, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
            if original_date != "N/A" else "N/A"
        )
        card_content += f"""
        <div style="margin-top: 20px; text-align: center; font-size: 18px;">
             <strong>Last Refreshed: </strong> {formatted_date}
        </div>
        """
        return ui.div(
            ui.HTML(card_content), 
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

        
        forex_columns = [col for col in df_combined.columns if col.startswith("exchange_rate")]
        df_corr = df_combined[["value"] + forex_columns]
        
        
        df_corr_numeric = df_corr.select_dtypes(include=[float, int])
        
        
        correlation_matrix = df_corr_numeric.corr()
        
        return correlation_matrix




    @output
    @render.ui
    def correlation_heatmap():
        
        correlation_matrix = calculate_forex_crude_correlation(df_crude_oil, df_forex)
        custom_colorscale = [
            [0, 'rgb(128, 0, 32)'],  # Dark Burgundy
            [0.25, 'rgb(200, 0, 50)'],  # Lighter Burgundy
            [0.5, 'rgb(255, 100, 100)'],  # Lighter Red
            [0.75, 'rgb(255, 200, 200)'],  # Very Light Red
            [1, 'rgb(255, 255, 255)']  # White (for max value)
        ]
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale=custom_colorscale,
            zmin=-1, zmax=1,
            colorbar=dict(title="Correlation Coefficient")
        ))
        
        fig_heatmap.update_layout(
            title="Correlation Heatmap: Crude Oil Prices vs Forex Exchange Rates",
            xaxis_title="Exchange Rates",
            yaxis_title="Crude Oil Price (USD)",
            template="plotly_white",
            title_font_size=20,
            margin=dict(l=40, r=40, t=60, b=40),
        )
        
        return ui.HTML(fig_heatmap.to_html(full_html=False))
