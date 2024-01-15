from io import StringIO 
from services.stock_manager.filler import fill_data
import pandas as pd
import os
import sys

# Add the parent directory of `data_extractor` to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def extract_data(product_filepath: str) -> pd.DataFrame:
    # Read the HTML content from the .xls file
    with open(f'./services/stock_manager/{product_filepath}', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Wrap the HTML content in a StringIO object
    html_buffer = StringIO(html_content)

    df = pd.read_html(html_buffer, header=8)[0]

    # Assuming 'df' is your original DataFrame with columns 'date' and 'sales'
    # Convert 'date' to a DateTime object and sort
    df['Fecha'] = df['Fecha'].str.replace('="', '').str.replace('"', '')
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
    df = df[["Fecha", "Entrada", "Salida", "Stock"]]

    # Aggregate sales data by day
    # Group by date and aggregate the data
    ohlc_data = df.groupby('Fecha').agg({
        'Stock': 'last',   # First stock value of the day as 'Open'
        'Entrada': 'sum',   # Sum of 'Entrada' for the day
        'Salida': 'sum',    # Sum of 'Salida' for the day
    }).rename(columns={'Stock': 'Close',
                    'Entrada': 'Purchases',
                    'Salida': 'Sales'})

    # Calculate 'Open' as 'Close' - sum('Purchases') + sum('Sales')
    ohlc_data['Open'] = ohlc_data['Close'] - ohlc_data['Purchases'] + ohlc_data['Sales']

    # Create columns 'High' and 'Low' and fill them with the possible min and max values of 'Stock' for each day
    ohlc_data['High'] = ohlc_data['Open'] + ohlc_data['Purchases']
    ohlc_data['Low'] = ohlc_data['Open'] - ohlc_data['Sales']

    # Handle missing dates (if necessary)
    all_dates = pd.date_range(start=ohlc_data.index.min(), end=ohlc_data.index.max(), freq='D')

    # Reindex the DataFrame to include all dates and fill missing dates with previous day's values
    ohlc_data = ohlc_data.reindex(all_dates)

    # Fill missing values with 0 for Entrada and Salida
    ohlc_data['Purchases'].fillna(0, inplace=True)
    ohlc_data['Sales'].fillna(0, inplace=True)

    # Forward fill Open and Close columns to propagate the last known values
    ohlc_data['Close'].fillna(method='ffill', inplace=True)
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

    fill_data(ohlc_data)

    return ohlc_data
