import pandas as pd

from services.stock_manager.data_extractor import data_extractor
from services.stock_manager.plotter import plot_data_and_recommendations
from services.stock_manager.simple.predictors import predict_units_to_buy
from services.stock_manager.distribution_estimator import get_sales_current_distribution

def predict(kardex):
    product_data: pd.DataFrame = data_extractor(kardex)
    recommendations = []
    for i in range(len(product_data) - 2, -1, -1):
        recommendation: int = predict_units_to_buy(product_data[:-i if i > 0 else None])
        recommendations.append(recommendation)

    mean, _, _, _ = get_sales_current_distribution(product_data)
    plot_data = plot_data_and_recommendations(product_data, recommendations)
    
    return plot_data, mean

def predict_no_plot(kardex):
    product_data: pd.DataFrame = data_extractor(kardex)
    recommendations = []
    for i in range(len(product_data) - 2, -1, -1):
        recommendation: int = predict_units_to_buy(product_data[:-i if i > 0 else None])
        recommendations.append(recommendation)

    return recommendations[-1], product_data.index[-1]