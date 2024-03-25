# necesito que este codigo dropee las tablas:
# public  | consumos                     | tabla | postgres
# public  | consumos_detalle             | tabla | postgres
# public  | despachos                    | tabla | postgres
# public  | devoluciones                 | tabla | postgres
# public  | documentos                   | tabla | postgres
# public  | documentos_detalle           | tabla | postgres
# public  | last_net_cost                | tabla | postgres
# public  | lista_precios                | tabla | postgres
# public  | officinas                    | tabla | postgres
# public  | product_supplier_association | tabla | postgres
# public  | productos                    | tabla | postgres
# public  | productos_stock              | tabla | postgres
# public  | recepciones                  | tabla | postgres
# public  | recepciones_detalle          | tabla | postgres
# public  | recomendaciones_del_dia      | tabla | postgres
# public  | suppliers                    | tabla | postgres
# public  | ventas                       | tabla | postgres
# public  | ventas_documentos            | tabla | postgres

from sqlalchemy import text
from databases.session import AppSession

def drop_table(table_name):
    with AppSession() as session:
        session.execute(text(f"DROP TABLE {table_name}"))
        session.commit()
        print(f"Tabla {table_name} eliminada exitosamente.")

tablas = ['consumos_detalle', 'consumos', 'despachos', 'devoluciones', 'documentos_detalle', 'ventas_documentos', 'documentos', 'last_net_cost', 'lista_precios', 'officinas', 'product_supplier_association', 'productos_stock', 'recomendaciones_del_dia', 'recepciones_detalle', 'productos', 'recepciones', 'suppliers', 'ventas']

for tabla in tablas:
    drop_table(tabla)