import os
import sys
import time
import pandas as pd

def data_extractor(kardex):
    df = kardex
    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y/%m/%d %H:%M:%S')
    df['fecha'] = df['fecha'].dt.normalize()

    df['ventas'] = df.apply(lambda x: x['salida'] if x['tipo_salida'] == 'venta' else 0, axis=1)

    ohlc_data = df.groupby('fecha').agg({
        'stock_actual': 'last',
        'entrada': 'sum',
        'salida': 'sum',  # Total outflows
        'ventas': 'sum',  # Sum of sales quantities specifically
    }).rename(
        columns={
            'stock_actual': 'Close', 
            'entrada': 'Purchases', 
            'salida': 'Outflow',  # Total outflows including sales
            'ventas': 'Sales'  # Sum of sales quantities
        }
    )
    
    ohlc_data['Open'] = ohlc_data['Close'] - ohlc_data['Purchases'] + ohlc_data['Outflow']
    ohlc_data['High'] = ohlc_data['Open'] + ohlc_data['Purchases']
    ohlc_data['Low'] = ohlc_data['Open'] - ohlc_data['Outflow']

    today = [time.strftime("%Y-%m-%d %H:%M:%S")]
    today_df = pd.DataFrame(today, columns=['fecha'])
    today_df['fecha'] = pd.to_datetime(today_df['fecha'], format='%Y-%m-%d %H:%M:%S')
    today_df['fecha'] = today_df['fecha'].dt.normalize()

    # print(ohlc_data.index.min(), type(ohlc_data.index.min()))
    # print(today_df['fecha'].iloc[0], type(today_df['fecha'].iloc[0]))
    # print(ohlc_data.index.max(), type(ohlc_data.index.max()))

    all_dates = pd.date_range(start=ohlc_data.index.min(), end=today_df['fecha'].iloc[0], freq='D')
    ohlc_data = ohlc_data.reindex(all_dates)

    ohlc_data['Purchases'].fillna(0, inplace=True)
    ohlc_data['Outflow'].fillna(0, inplace=True)

    ohlc_data['Close'].ffill(inplace=True)
    ohlc_data['Open'].fillna(ohlc_data['Close'], inplace=True)

    ohlc_data['High'].fillna(ohlc_data['Open'], inplace=True)
    ohlc_data['Low'].fillna(ohlc_data['Close'], inplace=True)
    ohlc_data.fillna(0, inplace=True)

    ohlc_data.index = pd.to_datetime(ohlc_data.index)

    ohlc_data['Close'].fillna(0, inplace=True)

    ohlc_data.index = pd.to_datetime(ohlc_data.index)
    
    return ohlc_data
