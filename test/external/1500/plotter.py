import pandas as pd
import os
import plotly.graph_objects as go

class TestAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def read_excel(self):
        try:
            self.df = pd.read_excel(self.file_path)
            print("Lectura exitosa. DataFrame creado.")
            # print(self.df)
        except FileNotFoundError:
            print(f"El archivo '{self.file_path}' no se encuentra en la ruta especificada.")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")

    def plot_candlestick(self, title='Gráfico de Velas Japonesas'):
        if self.df is not None:
            try:
                fig = go.Figure(data=[go.Candlestick(x=self.df['Unnamed: 0'],
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

    def statistic_info(self):
        if self.df is not None:
            total_days = len(self.df)
            start_date = self.df.iloc[0]['Unnamed: 0']
            end_date = self.df.iloc[-1]['Unnamed: 0']
            zero_close_days = len(self.df[self.df['Close'] == 0])
            mean_sales = self.df['Sales'].mean()

            print(f"Total de días del análisis: {total_days}")
            print(f"Fecha de inicio: {start_date}")
            print(f"Fecha de fin: {end_date}")
            print(f"Días con stock en 0 (Close): {zero_close_days}")
            print(f"Media de ventas (Sales): {mean_sales}")

        else:
            print("El DataFrame no ha sido leído aún. Utiliza el método 'read_excel' primero.")

# Uso de la clase
if __name__ == "__main__":
    archivo = 'test/external/kardex.xlsx'
    plotter = TestAnalysis(archivo)
    plotter.read_excel()
    plotter.plot_candlestick(title='Gráfico de Velas Japonesas')
    plotter.statistic_info()
