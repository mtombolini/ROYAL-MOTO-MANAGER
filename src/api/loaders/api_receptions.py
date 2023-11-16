from sqlalchemy.orm import Session
from databases.session import DocumentSession
from models.receptions import Reception, ReceptionDetail

def save_receptions_to_db(df, session: Session):
    receptions = [
        Reception(
            id=row['id'],
            fecha=row['admissionDate'],
            documento=row['document'],
            nota=row['note']
        ) for _, row in df.iterrows()
    ]
    session.add_all(receptions)
    session.commit()

def save_reception_details_to_db(df, session: Session):
    for _, row in df.iterrows():
        detail_record = ReceptionDetail(
            id=row['id'],
            reception_id=row['reception_id'],
            cantidad=row['quantity'],
            costo_neto=row['cost'],
            variant_id=row['variant_id']
        )
        session.add(detail_record)
    session.commit()

async def fetch_and_save_receptions(api):
    recepciones_df, detalles_df = await api.obtener_recepciones()
    with DocumentSession() as session:
        save_receptions_to_db(recepciones_df, session)
        save_reception_details_to_db(detalles_df, session)
    print(f"Recepciones y detalles guardados en la base de datos.")
