from dataclasses import dataclass, field

@dataclass
class SilverTableConfig:
    """Configuration for Bronze -> Silver transformation """
    source_table: str           # acme_catalog.bronze.xxx
    target_table: str           # acme_catalog.silver.xxx
    table_description: str      # Description of the table
    key_columns: list[str]      # key for merge
    column_mapping: dict        # rename columns
    cast_columns: dict          # columns type
    required_columns: list[str] # required columns
    column_comments: dict       # Description of the columns

CATALOG = "acme_catalog"
SILVER_SCHEMA = "silver"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.{SILVER_SCHEMA}"

SILVER_CONFIG: dict[str, SilverTableConfig] = {
    "categories": SilverTableConfig(
        source_table=f"{BRONZE}.categories",
        target_table=f"{SILVER}.categories",
        table_description="Cleaned product categories with proper types",
        key_columns=["category_id"],
        column_mapping={
            "CategoryID": "category_id",
            "CategoryName": "category_name",
            "Description": "description",
        },
        cast_columns={
            "category_id": "integer",
            "category_name": "string",
            "description": "string",
        },
        required_columns=["category_id", "category_name"],
        column_comments={
            "category_id":   "Category unique ID",
            "category_name": "Category name",
            "description":   "Category description",
        },
    ),
    "customers": SilverTableConfig(
        source_table=f"{BRONZE}.customers",
        target_table=f"{SILVER}.customers",
        table_description="Cleaned customer master data with proper types",
        key_columns=["customer_id"],
        column_mapping={
            "CustomerID":     "customer_id",
            "CompanyName":    "company_name",
            "ContactName":    "contact_name",
            "City":           "city",
            "Country":        "country",
            "DivisionID":     "division_id",
            "Address":        "address",
            "Fax":            "fax",
            "Phone":          "phone",
            "PostalCode":     "postal_code",
            "StateProvince":  "state_province",
        },
        cast_columns={
            "customer_id":    "integer",
            "company_name":   "string",
            "contact_name":   "string",
            "city":           "string",
            "country":        "string",
            "division_id":    "integer",
            "address":        "string",
            "fax":            "string",
            "phone":          "string",
            "postal_code":    "string",
            "state_province": "string",
        },
        required_columns=["customer_id", "company_name", "country", "division_id"],
        column_comments={
            "customer_id":    "Customer unique ID",
            "company_name":   "Customer company name",
            "contact_name":   "Customer contact person",
            "city":           "Customer city",
            "country":        "Customer country",
            "division_id":    "FK to divisions",
            "address":        "Customer address",
            "fax":            "Customer fax",
            "phone":          "Customer phone",
            "postal_code":    "Customer postal code",
            "state_province": "Customer state/province",
        },
    ),

    "divisions": SilverTableConfig(
        source_table=f"{BRONZE}.divisions",
        target_table=f"{SILVER}.divisions",
        table_description="Cleaned divisions with proper types",
        key_columns=["division_id"],
        column_mapping={
            "DivisionID":   "division_id",
            "DivisionName": "division_name",
        },
        cast_columns={
            "division_id":   "integer",
            "division_name": "string",
        },
        required_columns=["division_id", "division_name"],
        column_comments={
            "division_id":   "Division unique ID",
            "division_name": "Division/region name",
        },
    ),

    "order_details": SilverTableConfig(
        source_table=f"{BRONZE}.order_details",
        target_table=f"{SILVER}.order_details",
        table_description="Cleaned order details with proper types",
        key_columns=["order_id", "line_no"],
        column_mapping={
            "OrderID":   "order_id",
            "LineNo":    "line_no",
            "ProductID": "product_id",
            "Quantity":  "quantity",
            "UnitPrice": "unit_price",
            "Discount":  "discount",
        },
        cast_columns={
            "order_id":   "integer",
            "line_no":    "integer",
            "product_id": "integer",
            "quantity":   "integer",
            "unit_price": "decimal(10,4)",
            "discount":   "decimal(3,2)",
        },
        required_columns=["order_id", "line_no", "product_id", "quantity", "unit_price"],
        column_comments={
            "order_id":   "FK to orders",
            "line_no":    "Order line number",
            "product_id": "FK to products",
            "quantity":   "Quantity ordered",
            "unit_price": "Unit price at order time",
            "discount":   "Discount fraction applied (0-1)",
        },
    ),

    "orders": SilverTableConfig(
        source_table=f"{BRONZE}.orders",
        target_table=f"{SILVER}.orders",
        table_description="Cleaned orders with proper types",
        key_columns=["order_id"],
        column_mapping={
            "OrderID":     "order_id",
            "OrderDate":   "order_date",
            "CustomerID":  "customer_id",
            "EmployeeID":  "employee_id",
            "ShipperID":   "shipper_id",
            "Freight":     "freight",
        },
        cast_columns={
            "order_id":    "integer",
            "order_date":  "date",
            "customer_id": "integer",
            "employee_id": "integer",
            "shipper_id":  "integer",
            "freight":     "decimal(10,2)",
        },
        required_columns=["order_id", "order_date", "customer_id", "employee_id", "shipper_id"],
        column_comments={
            "order_id":    "Order unique ID",
            "order_date":  "Date order was placed",
            "customer_id": "FK to customers",
            "employee_id": "Employee who processed order",
            "shipper_id":  "FK to shippers",
            "freight":     "Freight/shipping cost",
        },
    ),

    "products": SilverTableConfig(
        source_table=f"{BRONZE}.products",
        target_table=f"{SILVER}.products",
        table_description="Cleaned products with proper types",
        key_columns=["product_id"],
        column_mapping={
            "ProductID":       "product_id",
            "ProductName":     "product_name",
            "SupplierID":      "supplier_id",
            "CategoryID":      "category_id",
            "QuantityPerUnit": "quantity_per_unit",
            "UnitCost":        "unit_cost",
            "UnitPrice":       "unit_price",
            "UnitsInStock":    "units_in_stock",
            "UnitsOnOrder":    "units_on_order",
        },
        cast_columns={
            "product_id":       "integer",
            "product_name":     "string",
            "supplier_id":      "integer",
            "category_id":      "integer",
            "quantity_per_unit":"integer",
            "unit_cost":        "decimal(10,4)",
            "unit_price":       "decimal(10,4)",
            "units_in_stock":   "integer",
            "units_on_order":   "integer",
        },
        required_columns=["product_id", "product_name", "category_id", "unit_cost", "unit_price"],
        column_comments={
            "product_id":        "Product unique ID",
            "product_name":      "Product name",
            "supplier_id":       "Supplier ID",
            "category_id":       "FK to categories",
            "quantity_per_unit": "Packaging quantity per unit",
            "unit_cost":         "Cost per unit (used for margin calculation)",
            "unit_price":        "Selling price per unit",
            "units_in_stock":    "Current stock quantity",
            "units_on_order":    "Quantity on order from supplier",
        },
    ),

    "shipments": SilverTableConfig(
        source_table=f"{BRONZE}.shipments",
        target_table=f"{SILVER}.shipments",
        table_description="Cleaned shipments with proper types",
        key_columns=["order_id", "line_no"],
        column_mapping={
            "OrderID":      "order_id",
            "LineNo":       "line_no",
            "ShipperID":    "shipper_id",
            "CustomerID":   "customer_id",
            "ProductID":    "product_id",
            "EmployeeID":   "employee_id",
            "ShipmentDate": "shipment_date",
        },
        cast_columns={
            "order_id":      "integer",
            "line_no":       "integer",
            "shipper_id":    "integer",
            "customer_id":   "integer",
            "product_id":    "integer",
            "employee_id":   "integer",
            "shipment_date": "date",
        },
        required_columns=["order_id", "line_no", "shipper_id", "customer_id", "product_id", "employee_id", "shipment_date"],
        column_comments={
            "order_id":      "FK to orders",
            "line_no":       "FK to order_details line",
            "shipper_id":    "FK to shippers",
            "customer_id":   "Customer ID (denormalized from orders)",
            "product_id":    "Product ID (denormalized from order_details)",
            "employee_id":   "Employee who processed shipment",
            "shipment_date": "Date line item was shipped",
        },
    ),

    "shippers": SilverTableConfig(
        source_table=f"{BRONZE}.shippers",
        target_table=f"{SILVER}.shippers",
        table_description="Cleaned shippers with proper types",
        key_columns=["shipper_id"],
        column_mapping={
            "ShipperID":   "shipper_id",
            "CompanyName": "company_name",
        },
        cast_columns={
            "shipper_id":   "integer",
            "company_name": "string",
        },
        required_columns=["shipper_id", "company_name"],
        column_comments={
            "shipper_id":   "Shipper unique ID",
            "company_name": "Shipper company name",
        },
    ),
}