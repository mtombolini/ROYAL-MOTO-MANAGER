# SERVICIOS

Esta carpeta contiene los servicios relacionados con el análisis de datos y la gestión de stock. 

## Descripción de los archivos

### analysis_main.py

Este archivo contiene la clase `Analyser` que se encarga de orquestar el proceso de análisis de stock. 

**Funcionalidades principales:**

- Obtiene los IDs de todos los productos.
- Obtiene los kardex de cada producto.
- Analiza los kardex utilizando el servicio de gestión de stock.
- Crea un modelo de recomendación diaria en base al análisis.

**Ejemplo de uso:**

```python
analyser = Analyser()
analyser.get_ids()
analyser.get_kardexs()
analyser.analyse()
session = AppSession()
analyser.create_model(session)
session.close()
```

### buys_analisys.py

Este archivo contiene la clase `BuysAnalysis` que se encarga del análisis de las compras.

**Funcionalidades principales:**

- Crea información sobre las compras, incluyendo fechas de pago, cantidades de productos y montos.
- Calcula el margen neto por compra y por producto.
- Evalúa las ventas por plazo de pago.
- Genera gráficos para visualizar el análisis.

**Ejemplo de uso:**

```python
buys = BuysAnalysis(cart_id)
buys.create_info()
margin_info = buys.calculate_net_margin_per_purchase()
margin_product_info = buys.calculate_net_margin_per_product()
sales_evaluation = buys.evaluate_sales_by_payment_term()
# ... (generación de gráficos)
```

### distribution_estimator.py

Este archivo contiene funciones para estimar la distribución de las ventas.

**Función principal:**

- `get_sales_current_distribution()`: Estima la media y la desviación estándar de las ventas a partir de los datos históricos.

**Ejemplo de uso:**

```python
mean, std, historic_mean, _, lower_bound_ci, upper_bound_ci, _ = get_sales_current_distribution(product_data)
```

### filler.py

Este archivo contiene la función `fill_data()` para rellenar los datos faltantes en el historial de ventas.

**Funcionalidad principal:**

- Simula las ventas para los días en los que no hay datos disponibles, utilizando una distribución normal basada en las ventas de los últimos 30 días.

**Ejemplo de uso:**

```python
filled_data = fill_data(data)
```

### parameters_service.py

Este archivo contiene las constantes de configuración para los servicios de gestión de stock.

**Constantes:**

- `CERTAINTY`: Nivel de certeza deseado para la predicción de agotamiento de stock.
- `CONFIDENCE_LEVEL`: Nivel de confianza para el intervalo de confianza.
- `DAYS_OF_ANTICIPATION`: Días de anticipación deseados para la compra de nuevas unidades.
- `DAYS_TO_LAST`: Días que se desea que duren las unidades compradas.
- `DOWN_COLOR`: Color para las velas bajistas en el gráfico.
- `UP_COLOR`: Color para las velas alcistas en el gráfico.
- `DECAY`: Factor de decaimiento para el cálculo de la media y la desviación estándar.
- `FEW_DATA_POINTS_PONDERATOR_LINEAR_COEFFICIENTS`: Coeficientes para la ponderación lineal en caso de pocos datos.

### plotter.py

Este archivo contiene la función `plot_data_and_recommendations()` para generar un gráfico con los datos históricos de ventas, las recomendaciones de compra y el stock actual.

**Funcionalidad principal:**

- Genera un gráfico de velas que muestra la evolución del stock a lo largo del tiempo.
- Superpone las recomendaciones de compra en el gráfico.

**Ejemplo de uso:**

```python
plot_data = plot_data_and_recommendations(product_data, recommendations)
```

### predictors.py

Este archivo contiene las funciones para predecir la necesidad de compra y la cantidad de unidades a comprar.

**Funciones principales:**

- `should_buy()`: Determina si es necesario comprar más unidades de un producto en función de la probabilidad de agotamiento de stock.
- `units_to_buy()`: Calcula la cantidad de unidades a comprar para que el stock dure un determinado número de días.

**Ejemplo de uso:**

```python
should_buy_ = should_buy(product_data, days_of_anticipation, certainty)
units_to_buy_ = units_to_buy(product_data, days_to_last)
```

### test.py

Este archivo contiene funciones para probar las funciones de predicción.

### data_extractor.py

Este archivo contiene la función `data_extractor` que se encarga de procesar los datos de un kardex y generar un DataFrame con la información relevante para el análisis de stock.

**Funcionalidad principal:**

- Convierte el kardex en un DataFrame con columnas para la fecha, el stock actual, las entradas, las salidas y las ventas.
- Calcula los valores de apertura, máximo y mínimo para cada día.
- Rellena los valores faltantes.

**Ejemplo de uso:**

```python
product_data: pd.DataFrame = data_extractor(kardex)
```

## Conclusión

La carpeta `/services` contiene un conjunto de servicios que se utilizan para analizar los datos de ventas y stock, generar recomendaciones de compra y visualizar los resultados. Estos servicios se utilizan en la aplicación principal para ayudar a los usuarios a gestionar su inventario de manera eficiente.