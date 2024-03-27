from models.office import Office
from models.returns import Return
from models.shipping import Shipping
from models.price_list import PriceList
from models.sales import Sale, SaleDocument
from models.supplier import Supplier, CreditTerm
from models.productos import Product, ProductStock
from models.document import Document, DocumentDetail
from models.reception import Reception, ReceptionDetail
from models.associations import product_supplier_association
from models.consumption import Consumption, ConsumptionDetail

from api.extractors.supplier_extractor import df_suppliers, df_connections

from random import randint

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

        self.df_price_list = None

        self.df_suppliers = df_suppliers
        self.df_connections = df_connections
        self.suppliers_id = []

        self.df_shippings = None

        self.df_offices = None

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

    def correct_price_list(self):
        self.df_price_list = self.df_price_list[
            self.df_price_list['Variant ID'].isin(self.df_products['Variant ID'])
        ]

    def create_shippings(self, session):
        for index, row in self.df_shippings.iterrows():
            shipping = Shipping(
                id = int(row['ID']),
                shipping_date = row['Shipping Date'],
                shipping_number = str(row['Shipping Number']),
                shipping_type = row['Shipping Type'],
                document_type = row['Document Type'],
                state = row['State']
            )
            session.add(shipping)

    def create_suppliers(self, session):
        for index, row in self.df_suppliers.iterrows():
            supplier = Supplier(
                rut = row['rut'],
                business_name = row['business_name'],
                trading_name = row['trading_name'],
                credit_term = CreditTerm(row['credit_term']),
                delivery_period = int(row['delivery_period'])
            )
            session.add(supplier)

    def create_products(self, session):
        for index, row in self.df_products.iterrows():
            product = Product(
                variant_id=int(row['Variant ID']),
                type=row['Product Type'],
                description=row['Product Description'],
                sku=row['SKU']
            )
            session.add(product)

    def create_products_suppliers(self, session):
        for index, row in self.df_connections.iterrows():
            product = session.query(Product).filter_by(sku=row['product_sku']).one_or_none()
            supplier = session.query(Supplier).filter_by(rut=row['supplier_rut']).one_or_none()
            
            if product and supplier:
                association = product_supplier_association.insert().values(
                    product_sku=product.sku,
                    supplier_rut=supplier.rut
                )
                session.execute(association)
        session.commit()
    
    def associate_unlinked_products_to_generic_supplier(self, session):
        generic_supplier = session.query(Supplier).filter_by(rut='00.000.000-0').one_or_none()
        all_products = session.query(Product).all()
        for product in all_products:
            if not product.suppliers:
                product.suppliers.append(generic_supplier)
        session.commit()


    def create_stocks(self, session):
        for index, row in self.df_stocks.iterrows():
            product_stock = ProductStock(
                variant_id=int(row['Variant ID']),
                stock_lira=int(row['Stock Lira 823']),
                stock_sobrexistencia=int(row['Stock Sobrexistencia'])
            )
            session.add(product_stock)

    def create_consumptions(self, session):
        for index, row in self.df_consumptions.iterrows():
            consumption = Consumption(
                id=int(row['ID']),
                date=row['Consumption Date'],
                office=row['Office'],
                note=row['Note']
            )
            session.add(consumption)

    def create_consumptions_details(self, session):
        for index, row in self.df_consumptions_details.iterrows():
            consumption_detail = ConsumptionDetail(
                id=int(row['Detail ID']),
                consumption_id=int(row['Consumption ID']),
                variant_id=int(row['Variant ID']),
                quantity=int(row['Quantity']),
                net_cost=float(row['Net Cost'])
            )
            session.add(consumption_detail)

    def create_receptions(self, session):
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

    def create_receptions_details(self, session):
        for index, row in self.df_receptions_details.iterrows():
            reception_detail = ReceptionDetail(
                id=int(row['Detail ID']),
                reception_id=int(row['Reception ID']),
                variant_id=int(row['Variant ID']),
                quantity=int(row['Quantity']),
                net_cost=float(row['Net Cost'])
            )
            session.add(reception_detail)

    def create_documents(self, session):
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

    def create_documents_details(self, session):
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

    def create_sales(self, session):
        for index, row in self.df_sales.iterrows():
            sale = Sale(
                id=int(row['Sales ID']),
                date=row['Sale Date'],
                payment_type=row['Payment Type']
            )
            session.add(sale)

    def create_sales_documents(self, session):
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

    def create_returns(self, session):
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

    def create_price_list(self, session):
        for index, row in self.df_price_list.iterrows():
            price_list = PriceList(
                list_id=int(row['List ID']),
                name=row['Name'],
                detail_id=int(row['Detail ID']),
                value=float(row['Value']),
                variant_id=int(row['Variant ID'])
            )
            session.add(price_list)

    def create_offices(self, session):
        for index, row in self.df_offices.iterrows():
            office = Office(
                id=int(row['ID']),
                name=row['Nombre'],
                address=row['Dirección'],
                municipality=row['Comuna'],
                city=row['Ciudad'],
                country=row['Pais'],
                active_state=row['Estado'],
                latitude=row['Latitud'],
                longitude=row['Longitud']
            )
            session.add(office)
    
    def create_data_base(self, session):
        self.correct_documents()
        self.correct_returns()
        self.correct_consumos()
        self.correct_recetions()
        self.correct_price_list()
        self.create_shippings(session)
        self.create_suppliers(session)
        self.create_offices(session)
        self.create_products(session)

        session.commit()

        self.create_products_suppliers(session)
        self.associate_unlinked_products_to_generic_supplier(session)
        self.create_stocks(session)
        self.create_consumptions(session)
        self.create_consumptions_details(session)
        self.create_receptions(session)
        self.create_receptions_details(session)
        self.create_documents(session)
        self.create_documents_details(session)
        self.create_sales(session)
        self.create_sales_documents(session)
        self.create_returns(session)
        self.create_price_list(session)

        session.commit()