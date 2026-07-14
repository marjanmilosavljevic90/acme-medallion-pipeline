from dataclasses import dataclass

from etl_config.constants_config import CATALOG, SILVER_SCHEMA, GOLD_SCHEMA, SILVER, GOLD, ColumnDef

__all__ = ["CATALOG", "SILVER_SCHEMA", "GOLD_SCHEMA", "SILVER", "GOLD", "ColumnDef", "FactConfig", "FACT_CONFIG"]


@dataclass
class FactConfig:
    """Configuration for Silver -> Gold fact table."""
    target_table: str
    table_description: str
    key_columns: list[str]
    columns: list[ColumnDef]
    source_query: str


FACT_CONFIG: dict[str, FactConfig] = {

    "fact_orders": FactConfig(
        target_table=f"{GOLD}.fact_orders",
        table_description="Gold fact: one row per order with freight and foreign keys to dimensions",
        key_columns=["order_id"],
        columns=[
            ColumnDef("order_id",    "INT",           nullable=False, comment="Order unique ID (natural key, PK)"),
            ColumnDef("customer_sk", "BIGINT",        nullable=True,  comment="FK to dim_customers (surrogate key)"),
            ColumnDef("shipper_sk",  "BIGINT",        nullable=True,  comment="FK to dim_shippers (surrogate key)"),
            ColumnDef("date_id",     "INT",           nullable=False, comment="FK to dim_date (format: yyyyMMdd)"),
            ColumnDef("order_date",  "DATE",          nullable=False, comment="Order date"),
            ColumnDef("freight",     "DECIMAL(10,2)", nullable=True,  comment="Freight cost for the order"),
        ],
        source_query=f"""
            with orders_resolved as (
                select
                    o.order_id,
                    o.order_date,
                    o.customer_id,
                    o.freight,
                    case
                        when coalesce(o.shipper_id, -1) not in (select shipper_id from {SILVER}.shippers) then -1
                        else coalesce(o.shipper_id, -1)
                    end as resolved_shipper_id
                from {SILVER}.orders o
            )
            select
                o.order_id, 
                dc.customer_sk, 
                ds.shipper_sk,
                dd.date_id,
                o.order_date, o.freight
            from orders_resolved o
            left join {GOLD}.dim_date dd
                on o.order_date = dd.full_date
            left join {GOLD}.dim_customers dc
                on o.customer_id = dc.customer_id and dc.is_current = true
            left join {GOLD}.dim_shippers ds
                on o.resolved_shipper_id = ds.shipper_id and ds.is_current = true
        """,
    ),

    "fact_order_lines": FactConfig(
        target_table=f"{GOLD}.fact_order_lines",
        table_description="Gold fact: one row per order line with revenue, cost and margin",
        key_columns=["order_id", "line_no"],
        columns=[
            ColumnDef("order_id",   "INT",           nullable=False, comment="FK to fact_orders (natural key)"),
            ColumnDef("line_no",    "INT",           nullable=False, comment="Order line number"),
            ColumnDef("product_sk", "BIGINT",        nullable=True,  comment="FK to dim_products (surrogate key)"),
            ColumnDef("quantity",   "INT",           nullable=False, comment="Quantity ordered"),
            ColumnDef("unit_price", "DECIMAL(10,4)", nullable=True,  comment="Unit price at order time"),
            ColumnDef("unit_cost",  "DECIMAL(10,4)", nullable=True,  comment="Unit cost from product master"),
            ColumnDef("discount",   "DECIMAL(3,2)",  nullable=True,  comment="Discount fraction applied (0-1)"),
            ColumnDef("revenue",    "DECIMAL(12,2)", nullable=True,  comment="quantity * unit_price * (1 - discount)"),
            ColumnDef("cost",       "DECIMAL(12,2)", nullable=True,  comment="quantity * unit_cost"),
            ColumnDef("margin",     "DECIMAL(12,2)", nullable=True,  comment="revenue - cost"),
        ],
        source_query=f"""
            select
                od.order_id, 
                od.line_no, 
                dp.product_sk, 
                od.quantity, 
                od.unit_price,
                p.unit_cost, od.discount,
                cast(od.quantity * od.unit_price * (1 - od.discount) as decimal(12,2)) as revenue,
                cast(od.quantity * p.unit_cost as decimal(12,2)) as cost,
                cast(od.quantity * od.unit_price * (1 - od.discount) - od.quantity * p.unit_cost as decimal(12,2)) as margin
            from {SILVER}.order_details od
            left join {SILVER}.products p on od.product_id = p.product_id -- for unit_cost
            left join {GOLD}.dim_products dp -- for product_sk
                on od.product_id = dp.product_id and dp.is_current = true
        """,
    ),

    "fact_shipments": FactConfig(
        target_table=f"{GOLD}.fact_shipments",
        table_description="Gold fact: one row per shipment line with shipper and shipment date",
        key_columns=["order_id", "line_no"],
        columns=[
            ColumnDef("order_id",         "INT",    nullable=False, comment="FK to fact_orders (natural key)"),
            ColumnDef("line_no",          "INT",    nullable=False, comment="FK to fact_order_lines line number"),
            ColumnDef("shipper_sk",       "BIGINT", nullable=True,  comment="FK to dim_shippers (surrogate key)"),
            ColumnDef("shipment_date_id", "INT",    nullable=False, comment="FK to dim_date for shipment date (format: yyyyMMdd)"),
            ColumnDef("shipment_date",    "DATE",   nullable=False, comment="Actual shipment date"),
        ],
        source_query=f"""
            select
                s.order_id, 
                s.line_no, 
                ds.shipper_sk,
                cast(date_format(s.shipment_date, 'yyyyMMdd') as int) as shipment_date_id,
                s.shipment_date
            from {SILVER}.shipments s
            left join {GOLD}.dim_shippers ds
                on s.shipper_id = ds.shipper_id and ds.is_current = true
        """,
    ),
}