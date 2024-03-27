import json
from databases.session import AppSession
from sqlalchemy import text

def transform_credit_term(credit_term):
    mapping = {
        'THIRTY_DAYS': '30 días',
        'SIXTY_DAYS': '60 días',
        'ONE_TWENTY_DAYS': '120 días',
        'RETURN': 'Devolución'
    }
    return mapping.get(credit_term, credit_term)

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
            if 'credit_term' in row_data:
                row_data['credit_term'] = transform_credit_term(row_data['credit_term'])
            data.append(row_data)
    
    with open(f"backup/{table_name}.json", 'w', encoding='latin-1') as f:
        f.write(json.dumps(data, indent=4))

get_json_data('product_supplier_association')
get_json_data('suppliers')