from models.productos import Product, ProductStock
from models.consumption import Consumption, ConsumptionDetail
from models.reception import Reception, ReceptionDetail
from models.document import Document, DocumentDetail
from models.sales import Sale, SaleDocument
from models.returns import Return

class DataFrameMain():
    def __init__(self):
        self.df_products = None
        self.df_stocks = None

        self.df_consumptions = None
        self.df_consumptions_details = None

        self.df_sales = None
        self.df_sales_documents = None

        self.df_documents = None
        self.df_documents_details = None

        self.df_receptions = None
        self.df_receptions_details = None

        self.df_returns = None

    def correct_products(self):
        self.df_products = self.df_products.dropna()

    def correct_documents(self):
        self.df_documents_details = self.df_documents_details[
            self.df_documents_details['Variant ID'].isin(self.df_products['Variant ID'])
        ]

    def correct_returns(self):
        self.df_returns = self.df_returns[
            self.df_returns['Document ID'].isin(self.df_documents['Document ID'])
        ]

    def correct_consumos(self):
        self.df_consumptions_details = self.df_consumptions_details[
            self.df_consumptions_details['Variant ID'].isin(self.df_products['Variant ID'])
        ]

    def correct_recetions(self):
        self.df_receptions_details = self.df_receptions_details[
            self.df_receptions_details['Variant ID'].isin(self.df_products['Variant ID'])
        ]
    
    def create_data_base(self, session):
        self.correct_documents()
        self.correct_returns()
        self.correct_consumos()
        self.correct_recetions()

        for index, row in self.df_products.iterrows():
            product = Product(
                variant_id=int(row['Variant ID']),
                type=row['Product Type'],
                description=row['Product Description'],
                sku=row['SKU']
            )
            session.add(product)

        for index, row in self.df_stocks.iterrows():
            product_stock = ProductStock(
                variant_id=int(row['Variant ID']),
                stock_lira=int(row['Stock Lira']),
                stock_sobrexistencia=int(row['Stock Sobrexistencia'])
            )
            session.add(product_stock)

        for index, row in self.df_consumptions.iterrows():
            consumption = Consumption(
                id=int(row['ID']),
                date=row['Consumption Date'],
                office=row['Office'],
                note=row['Note']
            )
            session.add(consumption)

        for index, row in self.df_consumptions_details.iterrows():
            consumption_detail = ConsumptionDetail(
                id=int(row['Detail ID']),
                consumption_id=int(row['Consumption ID']),
                variant_id=int(row['Variant ID']),
                quantity=int(row['Quantity']),
                net_cost=float(row['Net Cost'])
            )
            session.add(consumption_detail)

        for index, row in self.df_receptions.iterrows():
            reception = Reception(
                id=int(row['ID']),
                date=row['Admission Date'],
                document_type=row['Document'],
                document_number=row['Document Number'],
                office=row['Office'],
                note=row['Note']
            )
            session.add(reception)

        for index, row in self.df_receptions_details.iterrows():
            reception_detail = ReceptionDetail(
                id=int(row['Detail ID']),
                reception_id=int(row['Reception ID']),
                variant_id=int(row['Variant ID']),
                quantity=int(row['Quantity']),
                net_cost=float(row['Net Cost'])
            )
            session.add(reception_detail)

        for index, row in self.df_documents.iterrows():
            document = Document(
                id=int(row['Document ID']),
                date=row['Document Date'],
                document_number=row['Document Number'],
                office=row['Office'],
                total_amount=float(row['Total Amount']),
                net_amount=float(row['Net Amount']),
                document_type=row['Document Type']
            )
            session.add(document)

        for index, row in self.df_documents_details.iterrows():
            document_detail = DocumentDetail(
                id=int(row['Detail ID']),
                document_id=int(row['Document ID']),
                variant_id=int(row['Variant ID']),
                quantity=int(row['Quantity']),
                net_unit_value=float(row['Net Unit Value']),
                net_total_value=float(row['Net Total Value'])
            )
            session.add(document_detail)

        for index, row in self.df_sales.iterrows():
            sale = Sale(
                id=int(row['Sales ID']),
                date=row['Sale Date'],
                payment_type=row['Payment Type']
            )
            session.add(sale)

        for index, row in self.df_sales_documents.iterrows():
            if row['Document ID'] is not None:
                document_id = int(row['Document ID'])
            else:
                document_id = row['Document ID']

            sale_document = SaleDocument(
                id=int(row['ID Support']),
                sale_id=int(row['Sales ID']),
                document_id=document_id
            )
            session.add(sale_document)

        for index, row in self.df_returns.iterrows():
            if row['Credit Note ID'] is not None:
                credit_note_id = int(row['Credit Note ID'])
            else:
                credit_note_id = row['Credit Note ID']

            return_ = Return(
                id=int(row['Return ID']),
                document_id=int(row['Document ID']),
                credit_note_id=credit_note_id
            )
            session.add(return_)

        session.commit()