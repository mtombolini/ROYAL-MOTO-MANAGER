# API

Este directorio contiene los extractores y los puntos finales de la API utilizados en el proyecto. Los extractores se encargan de obtener datos de diferentes fuentes y procesarlos para su uso en la aplicación.

## Estructura del Directorio

- `extractors/`: Contiene los extractores de datos.
- `get/`: Contiene los puntos finales GET de la API, especificamente para la busqueda de productos.
- `post/`: Contiene los puntos finales POST de la API, especificamente para enviar las recepciones.

## Extractores

### AbstractExtraction

Ubicación: [`api/extractors/abstract_extraction.py`](extractors/abstract_extraction.py)

El `AbstractExtraction` es una clase base abstracta para los extractores. Define métodos y propiedades comunes que son heredados por los extractores específicos. Algunas de sus funciones principales incluyen:

- `get_data()`: Método abstracto para obtener datos desde el endpoint de la API.
- `main_extraction(response)`: Método abstracto para procesar la respuesta de la API y extraer los datos principales.
- `create_main_dataframe(data)`: Método abstracto para crear el DataFrame principal con los datos extraídos.

### ProductExtractor

Ubicación: [`api/extractors/product_extractor.py`](extractors/product_extractor.py)

El `ProductExtractor` se encarga de obtener y procesar los datos de productos. Algunas de sus funciones principales incluyen:

- `get_data()`: Obtiene los datos de productos desde el endpoint de la API.
- `main_product_extraction(response)`: Procesa la respuesta de la API y extrae los datos principales.
- `create_main_product_dataframe(product)`: Crea el DataFrame principal con los datos de productos.
- `get_stocks()`: Obtiene los datos de stocks de productos.

### SalesExtractor

Ubicación: [`api/extractors/sales_extractor.py`](extractors/sales_extractor.py)

El `SalesExtractor` se encarga de obtener y procesar los datos de ventas. Algunas de sus funciones principales incluyen:

- `get_data()`: Obtiene los datos de ventas desde el endpoint de la API.
- `main_extraction(response)`: Procesa la respuesta de la API y extrae los datos principales.
- `create_main_dataframe(sale)`: Crea el DataFrame principal con los datos de ventas.
- `correction()`: Realiza correcciones en los datos extraídos.

### ReceptionExtractor

Ubicación: [`api/extractors/reception_extractor.py`](extractors/reception_extractor.py)

El `ReceptionExtractor` se encarga de obtener y procesar los datos de recepciones. Algunas de sus funciones principales incluyen:

- `get_data()`: Obtiene los datos de recepciones desde el endpoint de la API.
- `main_extraction(response)`: Procesa la respuesta de la API y extrae los datos principales.
- `create_main_dataframe(reception)`: Crea el DataFrame principal con los datos de recepciones.
- `create_detail_dataframe(reception)`: Crea el DataFrame de detalles de las recepciones.

### PriceListExtractor

Ubicación: [`api/extractors/price_list_extractor.py`](extractors/price_list_extractor.py)

El `PriceListExtractor` se encarga de obtener y procesar las listas de precios. Algunas de sus funciones principales incluyen:

- `get_data()`: Obtiene los datos de las listas de precios desde el endpoint de la API.
- `main_extraction(response)`: Procesa la respuesta de la API y extrae los datos principales.
- `create_main_dataframe(price_list)`: Crea el DataFrame principal con los datos de las listas de precios.

### DocumentExtractor

Ubicación: [`api/extractors/document_extractor.py`](extractors/document_extractor.py)

El `DocumentExtractor` se encarga de obtener y procesar los datos de documentos. Algunas de sus funciones principales incluyen:

- `get_data()`: Obtiene los datos de documentos desde el endpoint de la API.
- `main_extraction(response)`: Procesa la respuesta de la API y extrae los datos principales.
- `create_main_dataframe(document)`: Crea el DataFrame principal con los datos de documentos.
- `create_detail_dataframe(document)`: Crea el DataFrame de detalles de los documentos.

## Post
### ReceptionPost

Ubicación: [`api/post/reception_post.py`](post/reception_post.py)

El `ReceptionPost` se encarga de enviar datos de recepciones a la API. Algunas de sus funciones principales incluyen:

- `make_request(endpoint, method="POST", data=None)`: Realiza una solicitud a la API.
- `send_data(post_data)`: Envía los datos de recepciones a la API.


## Get
### ProductGet

Ubicación: [`api/get/product_get.py`](get/product_get.py)

El `ProductGet` se encarga de obtener datos de productos desde la API. Algunas de sus funciones principales incluyen:

- `fetch_data()`: Realiza una solicitud GET a la API para obtener los datos de productos.
- `process_response(response)`: Procesa la respuesta de la API y extrae los datos relevantes.