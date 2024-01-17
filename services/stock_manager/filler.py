import numpy as np
import pandas as pd

def fill_data(data: pd.DataFrame) -> pd.DataFrame:
    days_without_stock = data['Sales'] == 0

    # Loop through each day without stock
    for date in data[days_without_stock].index:
        # Get available days with sales before the current date
        available_days = data.loc[(data.index <= date) & (data['Sales'] > 0)]

        # Determine the number of days to consider (up to 30 or the number of available days)
        days_to_consider = min(len(available_days), 30)

        # Extract the last 'days_to_consider' days
        last_30_days = available_days[-days_to_consider:]
        
        # Calculate mean and standard deviation
        mean_sales = last_30_days['Sales'].mean()
        std_sales = last_30_days['Sales'].std()

        # Simulate sales
        simulated_sale = np.random.normal(mean_sales, std_sales)
        simulated_sale = max(0, np.round(simulated_sale, 0))  # Ensure non-negative and round to nearest whole number

        # Replace the sales value for the day without stock
        data.at[date, 'Sales'] = simulated_sale
        
    return data
