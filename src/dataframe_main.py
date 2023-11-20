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

    def correct_documents(self):
        self.df_documents_details = self.df_documents_details[
            self.df_documents_details['Variant ID'].isin(self.df_products['Variant ID'])
        ]

    def correct_returns(self):
        self.df_returns = self.df_returns[
            self.df_returns['Document ID'].isin(self.df_documents['Document ID'])
        ]
    
    def create_data_base(self, session):
        self.correct_documents()
        self.correct_returns()

        for index, row in self.df_products.iterrows():
            product = Product(
                variant_id=row['Variant ID'],
                type=row['Product Type'],
                description=row['Product Description'],
                sku=row['SKU']
            )
            session.add(product)

        for index, row in self.df_stocks.iterrows():
            product_stock = ProductStock(
                variant_id=row['Variant ID'],
                stock_lira=row['Stock Lira'],
                stock_sobrexistencia=row['Stock Sobrexistencia']
            )
            session.add(product_stock)

        for index, row in self.df_consumptions.iterrows():
            consumption = Consumption(
                id=row['ID'],
                date=row['Consumption Date'],
                note=row['Note']
            )
            session.add(consumption)

        for index, row in self.df_consumptions_details.iterrows():
            consumption_detail = ConsumptionDetail(
                id=row['Detail ID'],
                consumption_id=row['Consumption ID'],
                variant_id=row['Variant ID'],
                quantity=row['Quantity'],
                net_cost=row['Net Cost']
            )
            session.add(consumption_detail)

        for index, row in self.df_receptions.iterrows():
            reception = Reception(
                id=row['ID'],
                date=row['Admission Date'],
                document_type=row['Document'],
                note=row['Note']
            )
            session.add(reception)

        for index, row in self.df_receptions_details.iterrows():
            reception_detail = ReceptionDetail(
                id=row['Detail ID'],
                reception_id=row['Reception ID'],
                variant_id=row['Variant ID'],
                quantity=row['Quantity'],
                net_cost=row['Net Cost']
            )
            session.add(reception_detail)

        for index, row in self.df_documents.iterrows():
            document = Document(
                id=row['Document ID'],
                date=row['Document Date'],
                total_amount=row['Total Amount'],
                net_amount=row['Net Amount'],
                document_type=row['Document Type']
            )
            session.add(document)

        for index, row in self.df_documents_details.iterrows():
            document_detail = DocumentDetail(
                id=row['Detail ID'],
                document_id=row['Document ID'],
                variant_id=row['Variant ID'],
                quantity=row['Quantity'],
                net_unit_value=row['Net Unit Value'],
                net_total_value=row['Net Total Value']
            )
            session.add(document_detail)

        for index, row in self.df_sales.iterrows():
            sale = Sale(
                id=row['Sales ID'],
                date=row['Sale Date'],
                payment_type=row['Payment Type']
            )
            session.add(sale)

        for index, row in self.df_sales_documents.iterrows():
            sale_document = SaleDocument(
                id=row['ID Support'],
                sale_id=row['Sales ID'],
                document_id=row['Document ID']
            )
            session.add(sale_document)

        for index, row in self.df_returns.iterrows():
            return_ = Return(
                id=row['Return ID'],
                document_id=row['Document ID'],
                credit_note_id=row['Credit Note ID']
            )
            session.add(return_)

        session.commit()