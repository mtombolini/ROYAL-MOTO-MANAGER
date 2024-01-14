from services.stock_manager.parameters import DOWN_COLOR, UP_COLOR
from typing import List
import plotly.graph_objects as go
import pandas as pd

def plot_data_and_recommendations(data: pd.DataFrame, recommendations: List[int]) -> None:
    # Create a figure for the candlestick chart
    fig = go.Figure()

    # Analyze each day and add buying recommendations
    i = 0
    for date, row in data.iloc[1:].iterrows():
        recommendation = recommendations[i]

        if recommendation != 0:
            # Add a marker for buying recommendation
            fig.add_trace(go.Scatter(x=[date], y=[row['High']],
                                     mode='markers', marker_symbol='triangle-up',
                                     text=f"Buy {recommendation} units",
                                     marker_color='blue', marker_size=10,
                                     name='Buy Recommendation'))
            
        i += 1

    # Add the candlestick trace
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 increasing_line_color=UP_COLOR,
                                 decreasing_line_color=DOWN_COLOR))

    # Update the figure layout
    fig.update_layout(title='Japanese Candlestick Chart with Buy Recommendations', yaxis_title='Cantidad')

    # Show the chart
    fig.show()
