import pandas as pd
from services.stock_manager.parameters_service import DECAY

from typing import Tuple

def get_sales_current_distribution(data: pd.DataFrame) -> Tuple[float]:
    """
    This function uses the last 30 recordings from sales' historical data 
    obtained from a pandas DataFrame, to estimate the mean and std of the sales.
    
    Args:
        data (pd.DataFrame): _description_

    Returns:
        _type_: _description_
    """
    days_to_consider = min(len(data), 30)

    # Extract the last 'days_to_consider' days
    not_all_days = data[data["Close"] != 0]

    last_30_days = not_all_days[-days_to_consider:]
    last_30_days = last_30_days[last_30_days["Close"] != 0]
    all_days = data[data["Close"] != 0]
    not_all_days = data[data["Close"] != 0]

    # Calculate mean and standard deviation
    mean_sales = last_30_days['Sales'].mean()
    std_sales = last_30_days['Sales'].std()

    historic_mean = all_days['Sales'].mean()
    historic_std = all_days['Sales'].std()
    
    return mean_sales, std_sales, historic_mean, historic_std

# def calculate_mean(sales: pd.Series) -> float:
#     sales_list = sales.tolist()
#     factors = [DECAY ** i for i in range(1, len(sales_list) + 1)]
#     factors.reverse()

#     suma = sum([sales_list[i] * factors[i] for i in range(len(sales_list))])
#     return suma / sum(factors)

# def calculate_std(sales: pd.Series) -> float:
#     mean = calculate_mean(sales)

#     sales_list = sales.tolist()
#     factors = [DECAY ** i for i in range(1, len(sales_list) + 1)]
#     factors.reverse()

#     suma = sum([((sales_list[i] - mean) ** 2) * factors[i] for i in range(len(sales_list))])

#     return (suma / sum(factors)) ** 0.5
