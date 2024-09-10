# MODELOS

Esta carpeta contiene las definiciones de los modelos de datos utilizados en la aplicación. Cada archivo `.py` define una o más clases que representan tablas en la base de datos y sus relaciones.


## cart.py

Este archivo define los modelos para los carros de compra y sus detalles:

* **`BuyCart`**: Representa un carro de compra.
    * `cart_id`: ID único del carro.
    * `descripcion`: Descripción del carro.
    * `fecha_creacion`: Fecha de creación del carro.
    * `fecha_recepcion`: Fecha de recepción del carro.
    * `proveedor`: Nombre del proveedor.
    * `rut`: RUT del proveedor.
    * `razon_social`: Razón social del proveedor.
    * `monto_neto`: Monto neto del carro.
    * `cantidad_productos`: Cantidad de productos en el carro.
    * `estado`: Estado del carro (e.g., "En proceso", "Recepcionada").
    * `revision`: Estado de revisión del carro.
    * `rendimiento`: Estado de rendimiento del carro.
    * `details`: Relación con los detalles del carro (uno a muchos).
    * `pay_dates`: Relación con las fechas de pago del carro (uno a muchos).

* **`BuyCartDetail`**: Representa un detalle de un carro de compra.
    * `id`: ID único del detalle.
    * `cart_id`: ID del carro al que pertenece el detalle.
    * `variant_id`: ID del producto variante.
    * `descripcion_producto`: Descripción del producto.
    * `sku_producto`: SKU del producto.
    * `costo_neto`: Costo neto del producto.
    * `cantidad`: Cantidad del producto.
    * `cart`: Relación con el carro al que pertenece el detalle (muchos a uno).


## consumption.py

Define los modelos para el registro de consumos:

* **`Consumption`**: Representa un registro de consumo.
    * `id`: ID único del consumo.
    * `date`: Fecha del consumo.
    * `office`: Oficina donde se realizó el consumo.
    * `note`: Nota o comentario sobre el consumo.
    * `details`: Relación con los detalles del consumo (uno a muchos).

* **`ConsumptionDetail`**: Representa un detalle de un consumo.
    * `id`: ID único del detalle.
    * `consumption_id`: ID del consumo al que pertenece el detalle.
    * `variant_id`: ID del producto consumido.
    * `quantity`: Cantidad consumida.
    * `net_cost`: Costo neto del producto consumido.
    * `consumption`: Relación con el consumo al que pertenece (muchos a uno).
    * `product`: Relación con el producto consumido (muchos a uno).


## day_recommendation.py

Define el modelo para las recomendaciones del día:

* **`DayRecommendation`**: Representa la recomendación de un producto para un día específico.
    * `variant_id`: ID del producto recomendado (clave primaria).
    * `recommendation`: Valor de la recomendación (e.g., 1, 2, 3).
    * `date`: Fecha de la recomendación.
    * `product`: Relación con el producto recomendado (uno a uno).

    **Métodos de clase:**
    * `get_all()`: Obtiene todas las recomendaciones del día, incluyendo información del producto y proveedor.
    * `filter_recommendations(search_query)`: Filtra las recomendaciones por variant_id, SKU, descripción del producto o nombre del proveedor.


## document.py

Define los modelos para documentos y sus detalles:

* **`Document`**: Representa un documento (e.g., factura, guía de despacho).
    * `id`: ID único del documento.
    * `date`: Fecha del documento.
    * `document_number`: Número del documento.
    * `office`: Oficina que emitió el documento.
    * `total_amount`: Monto total del documento.
    * `net_amount`: Monto neto del documento.
    * `document_type`: Tipo de documento (e.g., "Factura", "Guía de Despacho").
    * `details`: Relación con los detalles del documento (uno a muchos).
    * `sales`: Relación con las ventas asociadas al documento (uno a muchos).

* **`DocumentDetail`**: Representa un detalle de un documento.
    * `id`: ID único del detalle.
    * `document_id`: ID del documento al que pertenece el detalle.
    * `variant_id`: ID del producto en el detalle.
    * `quantity`: Cantidad del producto.
    * `net_unit_value`: Valor unitario neto del producto.
    * `net_total_value`: Valor total neto del producto (cantidad * valor unitario).
    * `document`: Relación con el documento al que pertenece (muchos a uno).
    * `product`: Relación con el producto en el detalle (muchos a uno).


## employee.py

Define el modelo para los empleados:

* **`Employee`**: Representa a un empleado.
    * `id`: ID único del empleado.
    * `user_id`: ID del usuario asociado al empleado (relación con la tabla 'usuarios').
    * `user`: Relación con el modelo `User`.
    * `run`: RUN del empleado.
    * `first_name`: Nombre del empleado.
    * `last_name`: Apellido del empleado.
    * `joined_in`: Fecha de ingreso del empleado.
    * `lunch_break`: Hora de inicio de la pausa para el almuerzo.
    * `overtime_hours`: Relación con los registros de horas extras del empleado.

    **Métodos de clase:**
    * `get_all()`: Obtiene una lista de todos los empleados con sus atributos.
    * `get(employee_id)`: Obtiene un empleado específico por su ID.
    * `create(**kwargs)`: Crea un nuevo empleado con los atributos proporcionados.
    * `edit(employee_id, **kwargs)`: Edita un empleado existente.
    * `delete(employee_id)`: Elimina un empleado.

    **Excepciones:**
    * `EmployeeNotFoundError`: Se lanza cuando no se encuentra un empleado.
    * `EmployeeAttributeNotFoundError`: Se lanza al intentar acceder a un atributo inexistente.


## last_net_cost.py

Define el modelo para el último costo neto de un producto:

* **`LastNetCost`**: Representa el último costo neto registrado para un producto.
    * `id`: ID único del registro.
    * `variant_id`: ID del producto al que se refiere el costo.
    * `net_cost_formated`: Costo neto formateado como cadena (e.g., "$1.234,56").
    * `net_cost`: Costo neto como número decimal.
    * `date`: Fecha del último costo neto registrado.
    * `product`: Relación con el producto al que se refiere (uno a uno).

    **Métodos de clase:**
    * `create_last_net_cost(variant_id, net_cost_formated, net_cost, date)`: Crea un nuevo registro de último costo neto.


## model_cart.py

Contiene una clase `ModelCart` que proporciona métodos para interactuar con los modelos `BuyCart` y `BuyCartDetail` en la base de datos.

**Métodos de clase:**
* `get_all_carts()`: Obtiene todos los carros de compra.
* `get_cart_by_id(cart_id)`: Obtiene un carro de compra por su ID.
* `get_receptioned_carts()`: Obtiene los carros de compra que han sido recepcionados.
* `delete_cart_by_id(cart_id)`: Elimina un carro de compra por su ID.
* `delete_cart_detail_by_id(cart_detail_id)`: Elimina un detalle de carro de compra por su ID.
* `get_cart_detail_by_id(cart_id)`: Obtiene los detalles de un carro de compra por su ID.
* `create_cart(cart_data)`: Crea un nuevo carro de compra.
* `create_cart_detail(cart_detail_data)`: Crea un nuevo detalle de carro de compra.
* `update_cart(cart_id, costo, cantidad)`: Actualiza el monto neto y la cantidad de productos de un carro de compra.
* `check_to_update_all_cart(cart_id)`: Verifica y actualiza el monto neto y la cantidad de productos de un carro de compra basándose en sus detalles.
* `update_cart_detail(cart_detail_id, cantidad, costo)`: Actualiza la cantidad y el costo de un detalle de carro de compra.
* `update_cart_status(cart_id, estado)`: Actualiza el estado de un carro de compra.
* `update_cart_datatime(cart_id, fecha_recepcion)`: Actualiza la fecha de recepción de un carro de compra.


## model_user.py

Contiene una clase `ModelUser` que proporciona métodos para interactuar con los modelos `User` y `Role` en la base de datos.

**Métodos de clase:**
* `login(username, password)`: Verifica las credenciales del usuario e inicia sesión si son válidas.
* `register(username, password, correo, nombre, apellido, id_role)`: Registra un nuevo usuario.
* `get_by_id(user_id)`: Obtiene un usuario por su ID.
* `get_all_roles()`: Obtiene todos los roles y sus usuarios asociados.
* `get_all_users()`: Obtiene todos los usuarios.
* `get_role_by_id(id_role)`: Obtiene un rol por su ID.
* `new_role(description)`: Crea un nuevo rol.
* `delete_role(id_role)`: Elimina un rol.
* `edit_role(id_role, new_description)`: Edita un rol.
* `delete_user(id_user)`: Elimina un usuario.
* `edit_user(user_id, username, correo, nombre, apellido, id_role)`: Edita un usuario.
* `is_superadmin(id_role)`: Verifica si un rol es "superadministrador".
* `is_user_the_superadmin(id_user)`: Verifica si un usuario tiene el rol "superadministrador".
* `role_has_associated_users(id_role)`: Verifica si un rol tiene usuarios asociados.


## office.py

Define el modelo para las oficinas:

* **`Office`**: Representa una oficina.
    * `id`: ID único de la oficina.
    * `name`: Nombre de la oficina.
    * `address`: Dirección de la oficina.
    * `municipality`: Municipio de la oficina.
    * `city`: Ciudad de la oficina.
    * `country`: País de la oficina.
    * `active_state`: Estado de activación de la oficina.
    * `latitude`: Latitud de la oficina.
    * `longitude`: Longitud de la oficina.

    **Métodos de clase:**
    * `get_all_offices()`: Obtiene una lista de todas las oficinas con sus atributos.


## overtime_hours.py

Define el modelo para registrar las horas extras de los empleados:

* **`OvertimeRecord`**: Representa un registro de horas extras de un empleado en un día específico.
    * `date`: Fecha del registro (clave primaria).
    * `employee`: Relación con el empleado al que pertenece el registro.
    * `employee_id`: ID del empleado (clave primaria).
    * `_check_in`: Hora de entrada registrada.
    * `_check_out`: Hora de salida registrada.
    * `_lunch_break_start`: Hora de inicio de la pausa para el almuerzo.
    * `_lunch_break_end`: Hora de fin de la pausa para el almuerzo.
    * `_confirmed`: Indica si el registro ha sido confirmado.
    * `_is_holiday`: Indica si el día es feriado.
    * `_is_on_vacation`: Indica si el empleado está de vacaciones.
    * `_absence`: Indica si el empleado estuvo ausente.

    **Propiedades:**
    * `is_holiday`, `confirmed`, `is_on_vacation`, `absence`, `employee_name`, `check_in`,
      `check_out`, `lunch_break_start`, `lunch_break_end`, `total_hours_worked`,
      `overtime_hours`, `is_late`, `leaves_early`, `hours_late`, `hours_early`.

    **Métodos:**
    * `is_working_day()`: Verifica si el día es un día laboral.
    * `was_worked()`: Verifica si el día fue trabajado.
    * `is_payable()`: Verifica si el día es pagable.
    * `is_saturday()`: Verifica si el día es sábado.
    * `is_sunday()`: Verifica si el día es domingo.
    * `get_column_values()`: Obtiene un diccionario con los valores de las columnas del registro.

    **Métodos de clase:**
    * `generate_standard_record_data(employee_id, date, session)`: Genera datos de registro estándar para un empleado en una fecha dada.
    * `get_employee_month_schedule_record(employee_id, month)`: Obtiene el registro de horario mensual de un empleado, incluyendo horas extras, totales, etc.
    * `create(session, **kwargs)`: Crea un nuevo registro de horas extras.
    * `edit(employee_id, date, **kwargs)`: Edita un registro de horas extras existente.
    * `delete(employee_id, month)`: Elimina un registro de horas extras.
    * `toggle_confirmed_status(employee_id, date)`: Cambia el estado de confirmación de un registro.
    * `toggle_is_holiday_status(employee_id, date)`: Cambia el estado de feriado de un registro.
    * `toggle_is_on_vacation_status(employee_id, date)`: Cambia el estado de vacaciones de un registro.
    * `toggle_absence_status(employee_id, date)`: Cambia el estado de ausencia de un registro.

    **Excepciones:**
    * `OvertimeRecordRecordNotFoundError`: Se lanza cuando no se encuentra el registro de horas extras de un empleado.
    * `OvertimeRecordRecordColumnNotFoundError`: Se lanza al intentar acceder a un atributo de registro inexistente.
    * `OvertimeRecordKeyError`: Se lanza cuando no se proporcionan las claves/identificadores necesarios para un nuevo registro.


## pay_dates.py

Define el modelo para las fechas de pago asociadas a un carro de compra:

* **`PayDates`**: Representa una fecha de pago para un carro de compra.
    * `id`: ID único de la fecha de pago.
    * `cart_id`: ID del carro de compra al que se asocia la fecha de pago.
    * `fecha_pago`: Fecha de pago.
    * `cart`: Relación con el carro de compra (muchos a uno).

    **Métodos de clase:**
    * `get_pay_dates(cart_id)`: Obtiene las fechas de pago asociadas a un carro de compra.
    * `delete_existing_dates(cart_id)`: Elimina las fechas de pago existentes para un carro de compra.
    * `create_new_dates(cart_id, dates)`: Crea nuevas fechas de pago para un carro de compra.


## price_list.py

Define el modelo para las listas de precios:

* **`PriceList`**: Representa una lista de precios.
    * `id`: ID único de la lista de precios.
    * `list_id`: ID de la lista.
    * `name`: Nombre de la lista de precios.
    * `detail_id`: ID del detalle de la lista.
    * `value`: Valor del precio en la lista.
    * `variant_id`: ID del producto al que se aplica el precio.
    * `product`: Relación con el producto (muchos a uno).

    **Métodos de clase:**
    * `get_price_list_by_variant_id(variant_id)`: Obtiene la lista de precios para un producto específico.


## product_activation.py

Define el modelo para la activación de productos:

* **`ProductActivation`**: Representa el estado de activación de un producto.
    * `id`: ID único del registro de activación.
    * `sku`: SKU del producto (único).
    * `is_active`: Estado de activación (booleano, True si está activo, False si no).

    **Métodos de clase:**
    * `get_product_activation_state(sku)`: Obtiene el estado de activación de un producto por su SKU.
    * `update_activation_state(sku, state)`: Actualiza el estado de activación de un producto.


## productos.py

Define los modelos para productos y su stock:

* **`Product`**: Representa un producto.
    * `variant_id`: ID único del producto (clave primaria).
    * `type`: Tipo de producto.
    * `description`: Descripción del producto.
    * `sku`: SKU del producto (único).
    * `stock`: Relación con el stock del producto (uno a uno).
    * `consumption_details`: Relación con los detalles de consumo (uno a muchos).
    * `reception_details`: Relación con los detalles de recepción (uno a muchos).
    * `document_details`: Relación con los detalles de documentos (uno a muchos).
    * `price_list`: Relación con la lista de precios (uno a muchos).
    * `day_recommendation`: Relación con la recomendación del día (uno a uno).
    * `last_net_cost`: Relación con el último costo neto (uno a uno).
    * `suppliers`: Relación con los proveedores (muchos a muchos).

    **Métodos de clase:**
    * `product_filter_by_id(variant_id)`: Obtiene un producto por su ID.
    * `product_filter_by_sku(sku)`: Obtiene un producto, el RUT de su proveedor y su último costo neto por su SKU.
    * `update_product_activation(variant_id)`: Actualiza el estado de activación de un producto.
    * `get_all_products_ids()`: Obtiene una lista de los IDs de todos los productos.
    * `get_all_products()`: Obtiene una lista de todos los productos con sus atributos.
    * `filter_products(search_query)`: Filtra los productos por ID, tipo, SKU, descripción o nombre del proveedor.
    * `filter_product(variant_id, analysis=True)`: Obtiene información detallada de un producto, incluyendo stock, recepciones, consumos, ventas, precios, etc.
    * `get_product_stock(variant_id)`: Obtiene el stock de un producto.
    * `get_product_reception(variant_id, len_dedit, normal_search=True)`: Obtiene los detalles de recepción de un producto.
    * `get_product_shipping(variant_id)`: Obtiene los detalles de envío de un producto.
    * `get_product_debit(variant_id)`: Obtiene los detalles de débito de un producto.
    * `get_product_comsumptions(variant_id)`: Obtiene los detalles de consumo de un producto.
    * `get_product_sales(variant_id)`: Obtiene los detalles de ventas de un producto.
    * `get_product_filtered_sales(variant_id, start_date, end_date)`: Obtiene los detalles de ventas de un producto dentro de un rango de fechas.
    * `get_product_price_list(variant_id, last_net_cost)`: Obtiene la lista de precios de un producto.
    * `update_product_supplier(variant_id, supplier_id)`: Actualiza el proveedor de un producto.

* **`ProductStock`**: Representa el stock de un producto.
    * `variant_id`: ID del producto al que pertenece el stock (clave primaria).
    * `stock_lira`: Stock en Lira.
    * `stock_sobrexistencia`: Stock en sobreexistencia.
    * `product`: Relación con el producto (uno a uno).

    **Métodos de clase:**
    * `get_all_stocks()`: Obtiene una lista de todos los stocks con sus atributos.
    * `filter_stock(variant_id)`: Obtiene el stock de un producto específico.


## reception.py

Define los modelos para las recepciones de productos:

* **`Reception`**: Representa una recepción de productos.
    * `id`: ID único de la recepción.
    * `date`: Fecha de la recepción.
    * `document_type`: Tipo de documento de la recepción (e.g., "Factura", "Guía de Despacho").
    * `document_number`: Número del documento de la recepción.
    * `office`: Oficina donde se realizó la recepción.
    * `note`: Nota o comentario sobre la recepción.
    * `details`: Relación con los detalles de la recepción (uno a muchos).

* **`ReceptionDetail`**: Representa un detalle de una recepción.
    * `id`: ID único del detalle.
    * `reception_id`: ID de la recepción a la que pertenece el detalle.
    * `variant_id`: ID del producto recibido.
    * `quantity`: Cantidad recibida.
    * `net_cost`: Costo neto del producto recibido.
    * `reception`: Relación con la recepción a la que pertenece (muchos a uno).
    * `product`: Relación con el producto recibido (muchos a uno).

    **Métodos de clase:**
    * `get_all_receptions_details()`: Obtiene todos los detalles de recepciones.
    * `filter_receptions_details_by_variant(variant_id)`: Filtra los detalles de recepciones por ID de producto.


## returns.py

Define el modelo para las devoluciones:

* **`Return`**: Representa una devolución.
    * `id`: ID único de la devolución.
    * `document_id`: ID del documento original asociado a la devolución.
    * `credit_note_id`: ID de la nota de crédito generada por la devolución (puede ser nulo).
    * `document`: Relación con el documento original (uno a uno).
    * `credit_note`: Relación con la nota de crédito (uno a uno).


## sales.py

Define los modelos para las ventas y su relación con los documentos:

* **`Sale`**: Representa una venta.
    * `id`: ID único de la venta.
    * `date`: Fecha de la venta.
    * `payment_type`: Tipo de pago de la venta.
    * `documents`: Relación con los documentos asociados a la venta (uno a muchos).

* **`SaleDocument`**: Representa la relación entre una venta y un documento.
    * `id`: ID único de la relación.
    * `sale_id`: ID de la venta.
    * `document_id`: ID del documento.
    * `sale`: Relación con la venta (muchos a uno).
    * `document`: Relación con el documento (muchos a uno).


## shipping.py

Define el modelo para los despachos:

* **`Shipping`**: Representa un despacho.
    * `id`: ID único del despacho.
    * `shipping_date`: Fecha del despacho.
    * `shipping_number`: Número del despacho.
    * `shipping_type`: Tipo de despacho.
    * `document_type`: Tipo de documento del despacho.
    * `state`: Estado del despacho.

    **Métodos de clase:**
    * `get_all_shippings()`: Obtiene todos los despachos.
    * `seach_shipping_guide_by_number(guide_number)`: Busca un despacho por su número de guía.


## supplier.py

Define el modelo para los proveedores:

* **`Supplier`**: Representa a un proveedor.
    * `id`: ID único del proveedor.
    * `rut`: RUT del proveedor (único).
    * `business_name`: Razón social del proveedor.
    * `trading_name`: Nombre comercial del proveedor.
    * `credit_term`: Plazo de crédito del proveedor (enum: `CreditTerm`).
    * `delivery_period`: Periodo de entrega del proveedor (en días).
    * `products`: Relación con los productos que proporciona el proveedor (muchos a muchos).

    **Métodos de clase:**
    * `create_from_df(supplier_df)`: Crea o actualiza proveedores a partir de un DataFrame.
    * `get_all()`: Obtiene una lista de todos los proveedores con sus atributos.
    * `get(supplier_id)`: Obtiene un proveedor específico por su ID.
    * `create(**kwargs)`: Crea un nuevo proveedor con los atributos proporcionados.
    * `edit(supplier_id, **kwargs)`: Edita un proveedor existente.
    * `delete(supplier_id)`: Elimina un proveedor.
    * `get_all_class()`: Obtiene una lista de todos los proveedores como objetos de la clase `Supplier`.

    **Excepciones:**
    * `SupplierNotFoundError`: Se lanza cuando no se encuentra un proveedor.
    * `SupplierAttributeNotFoundError`: Se lanza al intentar acceder a un atributo inexistente.


## user.py

Define los modelos para los usuarios y sus roles:

* **`User`**: Representa a un usuario.
    * `id`: ID único del usuario.
    * `username`: Nombre de usuario.
    * `_password`: Contraseña cifrada.
    * `nombre`: Nombre del usuario.
    * `apellido`: Apellido del usuario.
    * `correo`: Correo electrónico del usuario.
    * `id_role`: ID del rol del usuario.
    * `role`: Relación con el rol del usuario (muchos a uno).
    * `employee`: Relación con el empleado asociado al usuario (uno a uno).

    **Métodos:**
    * `check_password(password)`: Verifica si una contraseña coincide con la contraseña cifrada.

* **`Role`**: Representa un rol de usuario.
    * `id_role`: ID único del rol.
    * `description`: Descripción del rol.
    * `users`: Relación con los usuarios que tienen este rol (uno a muchos).


## Conclusión final de la carpeta /models

La carpeta `/models` es esencial para la aplicación, ya que define la estructura de datos y las relaciones entre las diferentes entidades que maneja el sistema. Cada archivo dentro de esta carpeta representa un aspecto específico del negocio, como productos, proveedores, clientes, ventas, compras, etc.

Los modelos están bien definidos, utilizando la librería SQLAlchemy para su representación como objetos de Python y su mapeo a la base de datos. Las relaciones entre los modelos (uno a uno, uno a muchos, muchos a muchos) se establecen correctamente, permitiendo una gestión eficiente de la información y la integridad de los datos.

Además de la estructura básica de las tablas, algunos modelos incluyen métodos de clase para realizar operaciones comunes, como obtener todos los registros, filtrar por ciertos criterios, crear nuevos registros, editarlos o eliminarlos. Estos métodos facilitan la interacción con la base de datos y promueven la reutilización de código.

En general, la carpeta `/models` presenta una organización clara, una estructura de datos bien definida y una implementación robusta que facilita el desarrollo y mantenimiento de la aplicación. 

**Puntos fuertes:**

* Modelos bien definidos y documentados.
* Relaciones entre modelos establecidas correctamente.
* Métodos de clase para operaciones comunes.
* Uso de SQLAlchemy para el mapeo objeto-relacional.

**Posibles mejoras:**

* Se podría considerar la implementación de más métodos de clase para realizar operaciones más complejas.
* Se podrían agregar validaciones de datos a nivel de modelo para asegurar la integridad de la información.
* Se podría mejorar la documentación de algunos modelos, incluyendo ejemplos de uso de los métodos de clase.

En resumen, la carpeta `/models` es una parte fundamental de la aplicación y proporciona una base sólida para el manejo de la información. Con algunas mejoras adicionales, se puede optimizar aún más su funcionalidad y facilitar su uso por parte de otros desarrolladores. 
