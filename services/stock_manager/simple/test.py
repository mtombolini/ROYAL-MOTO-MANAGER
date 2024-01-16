from services.stock_manager.data_extractor import extract_data, data_extractor
from services.stock_manager.simple.predictors import predict_units_to_buy
from services.stock_manager.plotter import plot_data_and_recommendations
import pandas as pd

product_filepath = "1705430809.xls"

# product_data: pd.DataFrame = extract_data(product_filepath)
# recommendations = []
# for i in range(len(product_data) - 2, -1, -1):
#     recommendation: int = predict_units_to_buy(product_data[:-i if i > 0 else None])
#     recommendations.append(recommendation)

# plot_data_and_recommendations(product_data, recommendations)

def predict(kardex):
    product_data: pd.DataFrame = data_extractor(kardex)
    recommendations = []
    for i in range(len(product_data) - 2, -1, -1):
        recommendation: int = predict_units_to_buy(product_data[:-i if i > 0 else None])
        recommendations.append(recommendation)

    plot_data = plot_data_and_recommendations(product_data, recommendations)
    return plot_data