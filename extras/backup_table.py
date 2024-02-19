from sqlalchemy import text
from databases.session import AppSession
from datetime import datetime

def export_table_data_to_sql(table_name):
    backup_file = f"backup/{table_name}_backup.sql"
    
    with open(backup_file, 'w') as f:
        with AppSession() as session:
            result = session.execute(text(f"SELECT * FROM {table_name}"))
            columns = result.keys()
            
            for row in result.fetchall():
                values = []
                for val in row:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, datetime):
                        # Formatear datetime a una cadena compatible con SQL
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif isinstance(val, str):
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    else:
                        values.append(str(val))
                
                values_str = ', '.join(values)
                f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values_str});\n")
    
    print(f"Respaldo de la tabla {table_name} completado exitosamente en {backup_file}.")


def import_table_data_from_sql(file_path):
    """Importa datos a la base de datos desde un archivo SQL."""
    with open(file_path, 'r') as file:
        sql_commands = file.read().split(';')[:-1]
        
        with AppSession() as session:
            for command in sql_commands:
                if command.strip():
                    session.execute(text(command))
            session.commit()
            print(f"Datos importados exitosamente desde {file_path}")

# Llamada a la función de exportación para tablas específicas
tablas_export = ['carros_compras', 'carros_compras_detalles']
for tabla in tablas_export:
    export_table_data_to_sql(tabla)

# tablas_import = ['carros_compras_backup.sql', 'carros_compras_detalles_backup.sql']
# for archivo in tablas_import:
#     import_table_data_from_sql(f"backup/{archivo}")
