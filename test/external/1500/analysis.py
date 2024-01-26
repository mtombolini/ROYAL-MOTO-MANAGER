import pandas as pd
import os
import plotly.express as px

class ExcelDataFramePlotter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def read_excel(self):
        try:
            self.df = pd.read_excel(self.file_path)
            print("Lectura exitosa. DataFrame creado.")
            print(self.df)
        except FileNotFoundError:
            print(f"El archivo '{self.file_path}' no se encuentra en la ruta especificada.")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")

    def plot_scatter(self, x_column, y_column, title='Gráfico de Dispersión'):
        if self.df is not None:
            try:
                fig = px.scatter(self.df, x=x_column, y=y_column, title=title)
                fig.show()
            except ValueError as ve:
                print(f"Error al generar el gráfico: {ve}")
        else:
            print("El DataFrame no ha sido leído aún. Utiliza el método 'read_excel' primero.")

# Uso de la clase
if __name__ == "__main__":
    archivo = 'test/external/kardex.xlsx'
    plotter = ExcelDataFramePlotter(archivo)
    plotter.read_excel()
    plotter.plot_scatter(x_column='Unnamed: 0', y_column='Close', title='Gráfico de Cierre')
