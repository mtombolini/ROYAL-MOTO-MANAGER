from typing import Tuple
import pandas as pd

def get_sales_current_distribution(data: pd.DataFrame) -> Tuple[float]:
    """
    This function uses the last 30 recordings from sales' historical data 
    obtained from a pandas DataFrame, to estimate the mean and std of the sales.
    
    Args:
        data (pd.DataFrame): _description_

    Returns:
        _type_: _description_
    """
    # Determine the number of days to consider (up to 30 or the number of available days)
    days_to_consider = min(len(data), 30)

    # Extract the last 'days_to_consider' days
    last_30_days = data[-days_to_consider:]
    
    # Calculate mean and standard deviation
    mean_sales = last_30_days['Sales'].mean()
    std_sales = last_30_days['Sales'].std()
    
    return mean_sales, std_sales
