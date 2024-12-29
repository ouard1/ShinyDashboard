\documentclass[a4paper,12pt]{article}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}

\title{Real-Time Dashboard for Crude Oil Analysis}
\author{Ouarda Boumansour \& Melissa Merabet}
\date{\today}

\begin{document}

\maketitle

\section{Overview}
This project implements a real-time dashboard that integrates and analyzes various datasets related to crude oil prices, forex exchange rates, and weather data. The dashboard allows users to interactively explore trends, correlations, and key insights through visualizations. Key features include:

\begin{itemize}
    \item \textbf{Crude Oil Price Analysis}: Visualize crude oil prices over time, including distributions and price fluctuations.
    \item \textbf{Forex Data Visualization}: Display the most recent forex exchange rates and their impact on crude oil prices.
    \item \textbf{Weather Data Integration}: Correlate weather variables like temperature and wind speed with crude oil price trends.
    \item \textbf{Correlation Analysis}: Examine the relationship between crude oil prices and forex exchange rates using heatmaps and scatter plots.
\end{itemize}

The data is fetched from multiple APIs and stored in MongoDB collections. The dashboard is built using a Shiny app (R) with interactive visualizations powered by Plotly.

\section{Data Sources}
\begin{itemize}
    \item \textbf{API Open-Meteo}: Supplies real-time weather data, including temperature and wind speed, used to analyze the impact of extreme weather on energy demand.
    \item \textbf{API Alpha Vantage (Forex Rates)}: Offers real-time forex rates for various currencies (USD, CAD, NOK, RUB, SAR).
    \item \textbf{API Alpha Vantage (Crude Oil Data)}: Supplies daily crude oil price data.
\end{itemize}

\section{Features}
\begin{itemize}
    \item \textbf{Interactive UI}: Select different years, months, regions, and weather variables to dynamically filter and display the data.
    \item \textbf{Crude Oil Price Trends}: A line plot and box plot to analyze crude oil price trends over time.
    \item \textbf{Forex Data Cards}: Display real-time forex exchange rates for selected currencies.
    \item \textbf{Weather vs. Crude Oil Prices}: A scatter plot showing the relationship between weather variables and crude oil prices.
    \item \textbf{Correlation Heatmap}: A heatmap that visualizes correlations between forex exchange rates and crude oil prices.
\end{itemize}

\section{Requirements}
\begin{itemize}
    \item Python 3.x
    \item Pandas
    \item Plotly
    \item Shiny (R)
    \item MongoDB
    \item APIs for data sources (Open-Meteo, Alpha Vantage)
\end{itemize}

\section{Setup Instructions}

\subsection{Clone the Repository}
Clone the project repository:
\begin{verbatim}
git clone https://github.com/ouard1/ShinyDashboard.git
cd ShinyDashboard
\end{verbatim}

\subsection{Install Python Dependencies}
Ensure you have Python 3.x installed. Then, install the required libraries:
\begin{verbatim}
pip install -r requirements.txt
\end{verbatim}

\subsection{Set Up MongoDB}
\begin{itemize}
    \item Set up a local or remote MongoDB instance.
    \item Populate the MongoDB collections (\texttt{crude\_oil\_data}, \texttt{forex\_data}, \texttt{weather\_data}, etc.) with data from the relevant APIs.
\end{itemize}

\subsection{Run the Shiny App}
To launch the dashboard, use the following command:
\begin{verbatim}
Rscript app.R
\end{verbatim}
This will start the Shiny server, and you can access the dashboard in your browser at \texttt{http://localhost:3838}.

\section{File Structure}
The project directory has the following structure:

\begin{verbatim}
real-time-dashboard-crude-oil
├── data/                 # Directory for raw and processed data
│   ├── raw/              # Raw data files
│      ├── weather_data/ 
│      ├── forex_data/ 
│      ├── crude_oil_data/ 
├── logs/                 # Directory for logs
├── scripts/              # Scripts for data collection and analysis
│   ├── collect_data.sh   # Script to collect data from APIs
│   ├── summarize.py      # Script to process data
│   └── analyze.py        # Script for data analysis and correlation calculations
├── dashboard/            # Shiny app files
│   └── app.py            # Shiny app server logic and UI
│   └── server.py         # Shiny app server logic 
│   └── ui.py             # Shiny app UI
├── report/               # Documentation and project report
│   └── report.md         # Project report file
├── cronjobs/             # Cron job configurations for automating data updates
│   └── crontab.txt       # Cron job file for updating data from APIs
└── requirements.txt      # Python dependencies for the project
\end{verbatim}

\section{Usage}
\begin{itemize}
    \item \textbf{Year and Month Selection}: Use the dropdown to select a specific year or month for filtering the crude oil price data.
    \item \textbf{Region Selection}: Choose a region from the dropdown to view data relevant to that region.
    \item \textbf{Weather Variables}: Select either temperature or wind speed to see how they correlate with crude oil prices.
    \item \textbf{Forex Exchange Rate}: View the most recent exchange rates for different currencies and their impact on crude oil prices.
\end{itemize}

\end{document}
