import json
from databases.session import AppSession
from sqlalchemy import text

def get_json_data(table_name):
    with AppSession() as session:
        result = session.execute(text(f"SELECT * FROM {table_name}"))
        # ALL COLUMNS EXCEPT ID IF IT EXISTS
        columns = list(result.keys())

        if 'id' in columns:
            id_index = columns.index('id')
        else:
            id_index = None

        data = []
        for row in result.fetchall():
            row_data = dict((col, row[i]) for i, col in enumerate(columns) if i != id_index)
            data.append(row_data)
    
    with open(f"backup/{table_name}.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

get_json_data('product_supplier_association')
get_json_data('suppliers')