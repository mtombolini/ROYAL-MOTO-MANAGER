import warnings
import pandas as pd

from math import ceil
from scipy.stats import norm

from services.stock_manager.parameters_service import CERTAINTY, DAYS_OF_ANTICIPATION, DAYS_TO_LAST
from services.stock_manager.distribution_estimator import get_sales_current_distribution

warnings.filterwarnings("ignore", category=RuntimeWarning)

def should_buy(product_data: pd.DataFrame, days_of_anticipation: int, certainty: float) -> bool:
    """
    This function returns a bool telling whether you should buy more units
    of a product or not, based on its sales' historical recent data and
    the current available stock.

    Args:
        product_data (pd.DataFrame): A DataFrame containing the sales 
        and remaining stock's historical data.
        days_of_anticipation (int): Desired number of days in advance to purchase more units
        before they run out. 
        certainty (float): Desired certainty for the event of the stock running out before
        days_of_anticipation.

    Returns:
        bool: Whether the probability of the stock running out before days_of_anticipation
        is greater than certainty (in that case, more units should be bought).
    """
    # Get the current sales mean and std from the last 30 recorded days 
    # or as many days as there are available if it's less than 30
    mean, std, historic_mean, _ = get_sales_current_distribution(product_data)

    stock_left: int = product_data["Close"].iloc[-1]
    prob_of_running_out = 1 - norm.cdf(stock_left, loc=mean * days_of_anticipation, 
                                       scale=std * days_of_anticipation)

    return prob_of_running_out > certainty or int(stock_left) <= ceil(historic_mean)


def units_to_buy(product_data: pd.DataFrame, days_to_last: int) -> int:
    # Get the current sales mean and std from the last 30 recorded days 
    # or as many days as there are available if it's less than 30
    mean, std, historic_mean, _ = get_sales_current_distribution(product_data)

    if mean * std == 0:
        return historic_mean * days_to_last - product_data.iloc[-1]["Close"]

    return max(0, mean * days_to_last - product_data.iloc[-1]["Close"])


def predict_units_to_buy(product_data):
    to_buy = ceil(
        (
            should_buy(
                product_data, 
                days_of_anticipation=DAYS_OF_ANTICIPATION, 
                certainty=CERTAINTY
            ) * units_to_buy(product_data, days_to_last=DAYS_TO_LAST)
        )
    )
    
    return to_buy
