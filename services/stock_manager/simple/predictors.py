from services.stock_manager.parameters import CERTAINTY, DAYS_OF_ANTICIPATION, DAYS_TO_LAST
from services.stock_manager.distribution_estimator import get_sales_current_distribution
from scipy.stats import norm
import pandas as pd

def should_buy(product_data: pd.DataFrame, 
               days_of_anticipation: int, 
               certainty: float) -> bool:
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
    mean, std = get_sales_current_distribution(product_data)

    stock_left: int = product_data["Close"].iloc[-1]
    prob_of_running_out = 1 - norm.cdf(stock_left, 
                                       loc=mean*days_of_anticipation, 
                                       scale=std*days_of_anticipation)
    
    return prob_of_running_out > certainty or product_data.iloc[-1]["Close"] == 0


def units_to_buy(product_data: pd.DataFrame, days_to_last: int) -> int:
    # Get the current sales mean and std from the last 30 recorded days 
    # or as many days as there are available if it's less than 30
    mean, std = get_sales_current_distribution(product_data)

    return mean*days_to_last


def predict_units_to_buy(product_data):
    to_buy = (should_buy(product_data, days_of_anticipation=DAYS_OF_ANTICIPATION, certainty=CERTAINTY)
              * units_to_buy(product_data, days_to_last=DAYS_TO_LAST))
    
    return to_buy
