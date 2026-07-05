from dataclasses import dataclass

@dataclass
class BronzeTableConfig:
    """Configuration for Landing -> Bronze ingestion"""
    table_name: str    # acme.catalog.bronze.xxx
    table_description: str
    all_columns: list[str]
    required_columns: list[str]
    column_comments: dict[str, str]

CATALOG = "acme_catalog"
LANDING_SCHEMA = "landing"
BRONZE_SCHEMA = "bronze"
BRONZE = f"{CATALOG}.{BRONZE_SCHEMA}"

LANDING_DIR = f"/Volumes/{CATALOG}/{LANDING_SCHEMA}/raw_files"
PROCESSED_DIR = f"{LANDING_DIR}/processed"
FAILED_DIR = f"{LANDING_DIR}/failed"


ARCHIVE_DIR = f"/Volumes/{CATALOG}/{LANDING_SCHEMA}/raw_files/archive"
CHECKPOINT_DIR = f"/Volumes/{CATALOG}/{LANDING_SCHEMA}/_checkpoints/bronze_autoloader"

BRONZE_CONFIG: dict[str, BronzeTableConfig] = {
    "categories": BronzeTableConfig(
        table_name     = f"{BRONZE}.categories",
        table_description = "Raw product categories",
        all_columns      = ["CategoryID", "CategoryName", "Description"],
        required_columns = ["CategoryID", "CategoryName"],
        column_comments = {
            "CategoryID": "Category unique ID",
            "CategoryName": "Category name",
            "Description": "Category description",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "customers": BronzeTableConfig(
        table_name      = f"{BRONZE}.customers",
        table_description = "Raw customer master data",
        all_columns       = ["CustomerID", "CompanyName", "ContactName", "Address", "City", "PostalCode", "Country", "DivisionID", "Fax", "Phone", "StateProvince"],
        required_columns  = ["CustomerID", "CompanyName", "ContactName", "City", "Country", "DivisionID"],
        column_comments = {
            "CustomerID": "Customer unique ID",
            "CompanyName": "Customer company name",
            "ContactName": "Customer contact person",
            "City": "Customer city",
            "Country": "Customer country",
            "DivisionID": "FK to divisions",
            "Address": "Customer address",
            "Fax": "Customer fax",
            "Phone": "Customer phone",
            "PostalCode": "Customer postal code",
            "StateProvince": "Customer state/province",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "divisions": BronzeTableConfig(
        table_name     = f"{BRONZE}.divisions",
        table_description = "Raw divisions/region reference data",
        all_columns      = ["DivisionID", "DivisionName"],
        required_columns = ["DivisionID", "DivisionName"],
        column_comments  = {
            "DivisionID": "Division unique ID",
            "DivisionName": "Division/region name",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "order_details": BronzeTableConfig  (
        table_name      = f"{BRONZE}.order_details",
        table_description = "Raw order line items",
        all_columns       = ["OrderID", "LineNo", "ProductID", "Quantity", "UnitPrice", "Discount"],
        required_columns  = ["OrderID", "LineNo", "ProductID", "Quantity", "UnitPrice"],
        column_comments   = {
            "OrderID": "FK to orders",
            "LineNo": "Order line number",
            "ProductID": "FK to products",
            "Quantity": "Quantity ordered",
            "UnitPrice": "Unit price at order time",
            "Discount": "Discount fraction applied",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "orders": BronzeTableConfig(
        table_name      = f"{BRONZE}.orders",
        table_description = "Raw orders",
        all_columns       = ["OrderID", "OrderDate", "CustomerID", "EmployeeID", "ShipperID", "Freight"],
        required_columns  = ["OrderID", "OrderDate", "CustomerID"],
        column_comments   = {
            "OrderID": "Order unique ID",
            "OrderDate": "Date order was placed",
            "CustomerID": "FK to customers",
            "EmployeeID": "Employee who processed order",
            "ShipperID": "FK to shippers",
            "Freight": "Freight/shipping cost",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "products": BronzeTableConfig(
        table_name      = f"{BRONZE}.products",
        table_description = "Raw product master data",
        all_columns       = ["ProductID", "ProductName", "SupplierID", "CategoryID", "QuantityPerUnit", "UnitCost", "UnitPrice", "UnitsInStock", "UnitsOnOrder"],
        required_columns  = ["ProductID", "ProductName", "SupplierID", "CategoryID", "UnitCost", "UnitPrice"],
        column_comments   = {
            "ProductID": "Product unique ID",
            "ProductName": "Product name",
            "SupplierID": "Supplier ID",
            "CategoryID": "FK to categories",
            "QuantityPerUnit": "Packaging description",
            "UnitCost": "Cost per unit (used for margin)",
            "UnitPrice": "Selling price per unit",
            "UnitsInStock": "Stock quantity",
            "UnitsOnOrder": "Quantity on order from supplier",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "shipments": BronzeTableConfig(
        table_name     = f"{BRONZE}.shipments",
        table_description = "Raw shipment tracking data",
        all_columns      = ["OrderID", "LineNo", "ShipperID", "CustomerID",  "ProductID", "EmployeeID", "ShipmentDate"],
        required_columns = ["OrderID",  "LineNo", "ShipperID", "CustomerID", "EmployeeID", "ShipmentDate"],
        column_comments  = {
            "OrderID": "FK to orders",
            "LineNo": "FK to order_details line",
            "ShipperID": "FK to shippers",
            "CustomerID": "Customer ID (denormalized)",
            "ProductID": "Product ID (denormalized)",
            "EmployeeID": "Employee who processed shipment",
            "ShipmentDate": "Date line was shipped",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
    "shippers": BronzeTableConfig(
        table_name     = f"{BRONZE}.shippers",
        table_description = "Raw shipper reference data",
        all_columns      = ["ShipperID", "CompanyName"],
        required_columns = ["ShipperID", "CompanyName"],
        column_comments  = {
            "ShipperID": "Shipper unique ID",
            "CompanyName": "Shipper company name",
            "_source_file": "Original source Excel file name",
            "_ingested_at": "Ingestion timestamp",
            "_batch_id": "Unique ID for this ingestion run",
        },
    ),
}
