from shiny import render, reactive, ui
import pandas as pd
import plotly.express as px
from datetime import datetime
from pymongo import MongoClient
import plotly.graph_objects as go
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["dashboard_app_db"]
collection_crude_oil = db["crude_oil_prices"]
collection_forex = db["forex_rates"]


def load_crude_oil_data(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df

def preprocess_dataframe(df):
    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

def create_missing_dates(df):
    full_date_range = pd.date_range(start=df["date"].min(), end=pd.to_datetime('today'), freq='D')
    missing_dates = full_date_range.difference(df["date"])

    missing_df = pd.DataFrame(missing_dates, columns=["date"])
    missing_df['value'] = None  
    missing_df["year"] = missing_df["date"].dt.year
    missing_df["month"] = missing_df["date"].dt.month

    return missing_df

def combine_and_sort_data(df, missing_df):
    combined_df = pd.concat([df, missing_df], ignore_index=True)
    combined_df = combined_df.sort_values(by="date")
    combined_df["_id"] = range(1, len(combined_df) + 1)
    return combined_df

def interpolate_missing_values(df):
    df['value'] = df['value'].interpolate()
    return df

def load_and_process_crude_oil_data(collection):
    df = load_crude_oil_data(collection)
    df = preprocess_dataframe(df)
    missing_df = create_missing_dates(df)
    df = combine_and_sort_data(df, missing_df)
    df = interpolate_missing_values(df)
    return df

def load_forex_data(collection):
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df
    

df_crude_oil = load_and_process_crude_oil_data(collection_crude_oil)
df_forex = load_forex_data(collection_forex)


def server(input, output, session):
    unique_years = sorted(df_crude_oil["year"].unique())
    unique_months = range(1, 13)

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
            <div style="display: flex; flex-direction: column; gap: 20px;">
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