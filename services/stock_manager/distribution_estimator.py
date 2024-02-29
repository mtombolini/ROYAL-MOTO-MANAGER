from services.stock_manager.parameters_service import CONFIDENCE_LEVEL, DECAY
import pandas as pd
import scipy.stats as stats

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
    days_considered = len(last_30_days)
    
    # last_30_days = last_30_days[last_30_days["Close"] != 0]
    all_days = data[data["Open"] + data["Close"] != 0]

    # Calculate mean and standard deviation
    mean_sales = last_30_days['Sales'].mean()
    std_sales = last_30_days['Sales'].std(ddof=1)  # ddof=1 for sample std deviation

    # Historic data calculations
    historic_mean = all_days['Sales'].mean()
    historic_std = all_days['Sales'].std()

    # Handle missing data
    if pd.isna(mean_sales): mean_sales = 0
    if pd.isna(std_sales): std_sales = 0
    if pd.isna(historic_mean): historic_mean = 0
    if pd.isna(historic_std): historic_std = 0

    # Calculate the 95% CI for the mean sales
    degrees_freedom = days_to_consider - 1
    t_critical = stats.t.ppf((1 + CONFIDENCE_LEVEL) / 2, df=degrees_freedom)
    margin_of_error = t_critical * (std_sales / ((days_considered + 0.0000000000000000000000000000000000000000000001) ** 0.5))

    lower_bound_ci = mean_sales - margin_of_error
    upper_bound_ci = mean_sales + margin_of_error

    return mean_sales, std_sales, historic_mean, historic_std, lower_bound_ci, upper_bound_ci, days_considered

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
