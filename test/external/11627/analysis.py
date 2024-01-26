import pandas as pd
import os
import plotly.graph_objects as go
import plotly.io as pio 

from services.stock_manager.simple.predictors import predict_units_to_buy

class TestAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.recommendations = []  # Lista para almacenar las recomendaciones

    def read_excel(self):
        try:
            self.df = pd.read_excel(self.file_path)
            self.df.rename(columns={'Unnamed: 0': 'Fecha'}, inplace=True)  # Renombrar la columna
            print("Lectura exitosa. DataFrame creado.")
        except FileNotFoundError:
            print(f"El archivo '{self.file_path}' no se encuentra en la ruta especificada.")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")

    def plot_simple_candlestick(self, title='Gráfico de Velas Japonesas (Sin Rec.)'):
        if self.df is not None:
            try:
                fig = go.Figure(data=[go.Candlestick(x=self.df['Fecha'],
                    open=self.df['Open'],
                    high=self.df['High'],
                    low=self.df['Low'],
                    close=self.df['Close'])])

                fig.update_layout(
                    title=title,
                    xaxis_title='Fecha',
                    yaxis_title='Precio',
                    margin=dict(l=20, r=20, t=20, b=20)
                )

                fig.show()
            except Exception as e:
                print(f"Error al generar el gráfico de velas japonesas: {e}")
        else:
            print("El DataFrame no ha sido leído aún. Utiliza el método 'read_excel' primero.")

    def generate_recommendations(self):
        if self.df is not None:
            self.recommendations = []
            for i in range(len(self.df) - 2, -1, -1):
                recommendation = predict_units_to_buy(self.df[:-i if i > 0 else None])
                self.recommendations.append(recommendation)

    def plot_complex_candlestick(self, title='Gráfico de Velas Japonesas (Con Rec.)'):
        if self.df is not None and self.recommendations:
            fig = go.Figure()

            for i, (index, row) in enumerate(self.df.iterrows()):
                if i < len(self.recommendations):
                    recommendation = self.recommendations[i]

                    if recommendation != 0:
                        fig.add_trace(
                            go.Scatter(
                                x=[row['Fecha']], y=[row['Close']], mode='markers', marker_symbol='triangle-up',
                                text=f"Buy {int(recommendation)} units", marker_color='blue', marker_size=10,
                                name='Buy Recommendation'))

            fig.add_trace(
                go.Candlestick(
                    x=self.df['Fecha'], open=self.df['Open'], high=self.df['High'], low=self.df['Low'],
                    close=self.df['Close'], name=''))

            fig.update_layout(
                title=title,
                showlegend=True,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title='Fecha',
                yaxis_title='Precio'
            )

            fig.show()
        else:
            print("El DataFrame o las recomendaciones no están disponibles. Asegúrate de haber ejecutado 'read_excel' y 'generate_recommendations' primero.")

    def statistic_info(self):
        if self.df is not None:
            total_days = len(self.df)
            start_date = self.df.iloc[0]['Fecha']
            end_date = self.df.iloc[-1]['Fecha']
            zero_close_days = len(self.df[self.df['Close'] == 0])
            mean_sales_all = self.df['Sales'].mean()
            mean_sales_non_zero_close = self.df[self.df['Close'] != 0]['Sales'].mean()
            lost_sales = (mean_sales_non_zero_close - mean_sales_all) * total_days
            total_sales = self.df['Sales'].sum()
            total_purchases = self.df['Purchases'].sum()

            print(f"Total de días del análisis: {total_days}")
            print(f"Fecha de inicio: {start_date}")
            print(f"Fecha de fin: {end_date}")
            print(f"Días con cierre en 0 (Close): {zero_close_days}")
            print(f"Media de ventas (Sales) en todos los días: {mean_sales_all}")
            print(f"Media de ventas (Sales) en días con cierre distinto de 0: {mean_sales_non_zero_close}")
            print(f"Estimación de ventas perdidas: {lost_sales}")
            print(f"Número total de ventas: {total_sales}")
            print(f"Número total de compras: {total_purchases}")

        else:
            print("El DataFrame no ha sido leído aún. Utiliza el método 'read_excel' primero.")

    def analyze_recommendations(self):
        if self.df is not None and self.recommendations:
            analysis_df = pd.DataFrame(columns=['ID', 'Fecha', 'Cantidad_Recomendada', 'Cantidad_Vendida', 'Delta'])

            for i, recommendation in enumerate(self.recommendations):
                if recommendation > 0 and i + 30 < len(self.df):  # Asegurarse de que haya una recomendación y no se exceda el rango
                    fecha = self.df.iloc[i]['Fecha']
                    ventas_30_dias = self.df.iloc[i+1:i+31]['Sales'].sum()  # Ventas en los siguientes 30 días
                    delta = recommendation - ventas_30_dias  # Cantidad recomendada menos cantidad vendida

                    analysis_df.loc[len(analysis_df)] = [i+1, fecha, recommendation, ventas_30_dias, delta]

            # Guardar el DataFrame en un archivo Excel
            analysis_df.to_excel('analysis_recommendation.xlsx', index=False)
            print("Análisis exportado a 'analysis_recommendation.xlsx'.")

            return analysis_df
        else:
            print("El DataFrame o las recomendaciones no están disponibles.")
            return None



if __name__ == "__main__":
    archivo = 'test/external/11627/kardex.xlsx'
    plotter = TestAnalysis(archivo)
    plotter.read_excel()
    plotter.generate_recommendations()
    analysis_results = plotter.analyze_recommendations()
    if analysis_results is not None:
        print(analysis_results)
    plotter.plot_complex_candlestick()
    plotter.statistic_info()