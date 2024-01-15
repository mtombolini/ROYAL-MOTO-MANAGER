from statsmodels.tsa.arima_model import ARIMA
from io import StringIO 
import pandas as pd
import plotly.graph_objects as go

# Read the HTML content from the .xls file
file_path = "1704999709.xls"
with open('./services/sarima/1705000470.xls', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Wrap the HTML content in a StringIO object
html_buffer = StringIO(html_content)

df = pd.read_html(html_buffer, header=8)[0]

# Assuming 'df' is your original DataFrame with columns 'date' and 'sales'
# Convert 'date' to a DateTime object and sort
df['Fecha'] = df['Fecha'].str.replace('="', '').str.replace('"', '')
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
df = df[["Fecha", "Entrada", "Salida", "Stock"]]

df.to_csv("1.csv")

# Aggregate sales data by day
# Group by date and aggregate the data
ohlc_data = df.groupby('Fecha').agg({
    'Stock': 'last',   # First stock value of the day as 'Open'
    'Entrada': 'sum',   # Sum of 'Entrada' for the day
    'Salida': 'sum',    # Sum of 'Salida' for the day
}).rename(columns={'Stock': 'Close'})

# Calculate 'Open' as 'Close' - sum('Entrada') + sum('Salida')
ohlc_data['Open'] = ohlc_data['Close'] - ohlc_data['Entrada'] + ohlc_data['Salida']

ohlc_data.to_csv("2.csv")

# Create columns 'High' and 'Low' and fill them with the possible min and max values of 'Stock' for each day
ohlc_data['High'] = ohlc_data['Open'] + ohlc_data['Entrada']
ohlc_data['Low'] = ohlc_data['Open'] - ohlc_data['Salida']

# Handle missing dates (if necessary)
all_dates = pd.date_range(start=ohlc_data.index.min(), end=ohlc_data.index.max(), freq='D')

# Reindex the DataFrame to include all dates and fill missing dates with previous day's values
ohlc_data = ohlc_data.reindex(all_dates)

# Fill missing values with 0 for Entrada and Salida
ohlc_data['Entrada'].fillna(0, inplace=True)
ohlc_data['Salida'].fillna(0, inplace=True)

ohlc_data.to_csv("3.csv")

# Forward fill Open and Close columns to propagate the last known values
ohlc_data['Close'].fillna(method='ffill', inplace=True)
ohlc_data.to_csv("4.csv")
ohlc_data['Open'].fillna(ohlc_data['Close'], inplace=True)

# Fill missing values for High and Low with Open and Close
ohlc_data['High'].fillna(ohlc_data['Open'], inplace=True)
ohlc_data['Low'].fillna(ohlc_data['Close'], inplace=True)

# Fill any remaining NaN values with 0
ohlc_data.fillna(0, inplace=True)

# Reset index to make sure it's datetime
ohlc_data.index = pd.to_datetime(ohlc_data.index)

# The last row will have NaN in the 'Next Close' column, so you can optionally fill it with a specific value if needed
ohlc_data['Close'].fillna(0, inplace=True)  # Fill NaN with 0 (or any other value you prefer)

ohlc_data.index = pd.to_datetime(ohlc_data.index)

# Define the up and down colors
up_color = 'green'
down_color = 'red'

ohlc_data.to_csv("5.csv")

# Create a figure for the candlestick chart
fig = go.Figure(data=[go.Candlestick(x=ohlc_data.index,
                open=ohlc_data['Open'],
                high=ohlc_data['High'],
                low=ohlc_data['Low'],
                close=ohlc_data['Close'],
                increasing_line_color=up_color,
                decreasing_line_color=down_color)])

# Update the figure layout
fig.update_layout(title='Japanese Candlestick Chart', yaxis_title='Cantidad')

# Show the chart
fig.show()
