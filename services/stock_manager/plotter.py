import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go

from typing import List
from services.stock_manager.parameters_service import DOWN_COLOR, UP_COLOR

def plot_data_and_recommendations(data: pd.DataFrame, recommendations: List[int]) -> None:
    fig = go.Figure()

    i = 0
    for date, row in data.iloc[1:].iterrows():
        recommendation = recommendations[i]

        if recommendation != 0:
            fig.add_trace(
                go.Scatter(
                    x=[date], y=[row['Close']], mode='markers', marker_symbol='triangle-up', 
                    text=f"Buy {int(recommendation)} units", marker_color='blue', marker_size=5, 
                    name='Buy Recommendation'))

        i += 1

    fig.add_trace(
        go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], 
            close=data['Close'], increasing_line_color=UP_COLOR, decreasing_line_color=DOWN_COLOR, 
            name=''))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis_title='Cantidad'
    )
    
    return pio.to_json(fig)
