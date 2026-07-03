from dataclasses import dataclass, field

CATALOG = "acme_catalog"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

SILVER = f"{CATALOG}.{SILVER_SCHEMA}"
GOLD = f"{CATALOG}.{GOLD_SCHEMA}"


@dataclass
class ColumnDef:
    """Single column definition: name, SQL type, nullability, and comment."""
    name: str
    sql_type: str
    nullable: bool = True
    comment: str = ""


SCD2_COLUMNS: list[ColumnDef] = [
    ColumnDef("valid_from", "TIMESTAMP", nullable=False, comment="SCD2: record valid from timestamp"),
    ColumnDef("valid_to",   "TIMESTAMP", nullable=True,  comment="SCD2: record valid to timestamp (NULL = current record)"),
    ColumnDef("is_current", "BOOLEAN",   nullable=False, comment="SCD2: TRUE if this is the current active record"),
]


@dataclass
class DimConfig:
    """Configuration for Silver -> Gold dimension table."""
    target_table: str
    table_description: str
    natural_key: str
    business_columns: list[ColumnDef]
    source_query: str
    surrogate_key_name: str = ""
    tracked_columns: list[str] = field(default_factory=list)


DIM_CONFIG: dict[str, DimConfig] = {

    "dim_customers": DimConfig(
        target_table=f"{GOLD}.dim_customers",
        table_description="Gold SCD2 dimension: customer master with denormalized division/region",
        natural_key="customer_id",
        surrogate_key_name="customer_sk",
        tracked_columns=[
            "company_name", "contact_name", "city", "country",
            "division_id", "division_name",
        ],
        business_columns=[
            ColumnDef("customer_id",   "INT",    nullable=False, comment="Customer natural key from source"),
            ColumnDef("company_name",  "STRING", nullable=False, comment="Customer company name"),
            ColumnDef("contact_name",  "STRING", nullable=True,  comment="Customer contact person"),
            ColumnDef("city",          "STRING", nullable=True,  comment="Customer city"),
            ColumnDef("country",       "STRING", nullable=False, comment="Customer country (breakdown dimension)"),
            ColumnDef("division_id",   "INT",    nullable=False, comment="Division ID"),
            ColumnDef("division_name", "STRING", nullable=False, comment="Division name - Region (Europe, North America, Scandinavia, South America)"),
        ],
        source_query=f"""
            select
                c.customer_id, c.company_name, c.contact_name, c.city,
                c.country, c.division_id, d.division_name
            from {SILVER}.customers c
            left join {SILVER}.divisions d on c.division_id = d.division_id
        """,
    ),

    "dim_products": DimConfig(
        target_table=f"{GOLD}.dim_products",
        table_description="Gold SCD2 dimension: product master with denormalized category (product line)",
        natural_key="product_id",
        surrogate_key_name="product_sk",
        tracked_columns=["product_name", "category_id", "category_name", "quantity_per_unit"],
        business_columns=[
            ColumnDef("product_id",        "INT",    nullable=False, comment="Product natural key from source"),
            ColumnDef("product_name",      "STRING", nullable=False, comment="Product name"),
            ColumnDef("category_id",       "INT",    nullable=False, comment="Category ID"),
            ColumnDef("category_name",     "STRING", nullable=False, comment="Category name - Product Line (Womens Footwear, Sportswear...)"),
            ColumnDef("quantity_per_unit", "INT",    nullable=True,  comment="Packaging quantity per unit"),
        ],
        source_query=f"""
            select p.product_id, p.product_name, p.category_id, cat.category_name, p.quantity_per_unit
            from {SILVER}.products p
            left join {SILVER}.categories cat on p.category_id = cat.category_id
        """,
    ),

    "dim_shippers": DimConfig(
        target_table=f"{GOLD}.dim_shippers",
        table_description="Gold SCD2 dimension: shipper reference, includes -1 Unknown placeholder",
        natural_key="shipper_id",
        surrogate_key_name="shipper_sk",
        tracked_columns=["company_name"],
        business_columns=[
            ColumnDef("shipper_id",   "INT",    nullable=False, comment="Shipper natural key from source (-1 = Unknown)"),
            ColumnDef("company_name", "STRING", nullable=False, comment="Shipper company name"),
        ],
        source_query=f"""
            select shipper_id, company_name from {SILVER}.shippers
            union all
            select -1 as shipper_id, 'Unknown Shipper' as company_name
        """,
    ),

    "dim_date": DimConfig(
        target_table=f"{GOLD}.dim_date",
        table_description="Gold dimension: continuous date spine from min to max order_date",
        natural_key="date_id",
        surrogate_key_name="",
        tracked_columns=[],
        business_columns=[
            ColumnDef("date_id",     "INT",     nullable=False, comment="Date surrogate key (format: yyyyMMdd)"),
            ColumnDef("full_date",   "DATE",    nullable=False, comment="Full date value"),
            ColumnDef("year",        "INT",     nullable=False, comment="Calendar year"),
            ColumnDef("quarter",     "INT",     nullable=False, comment="Calendar quarter (1-4)"),
            ColumnDef("month",       "INT",     nullable=False, comment="Calendar month (1-12)"),
            ColumnDef("month_name",  "STRING",  nullable=False, comment="Month name (January, February...)"),
            ColumnDef("week",        "INT",     nullable=False, comment="Week of year"),
            ColumnDef("day_of_week", "STRING",  nullable=False, comment="Day name (Monday, Tuesday...)"),
            ColumnDef("is_weekend",  "BOOLEAN", nullable=False, comment="True if Saturday or Sunday"),
        ],
        source_query=f"""
            with date_range as (
                select min(order_date) as min_date, max(order_date) as max_date
                from {SILVER}.orders
            )
            select
                cast(date_format(d.full_date, 'yyyyMMdd') as int) as date_id,
                d.full_date,
                year(d.full_date) as year,
                quarter(d.full_date) as quarter,
                month(d.full_date) as month,
                date_format(d.full_date, 'MMMM') as month_name,
                weekofyear(d.full_date) as week,
                date_format(d.full_date, 'EEEE') as day_of_week,
                case when dayofweek(d.full_date) in (1, 7) then true else false end as is_weekend
            from date_range
            cross join lateral (
                select explode(sequence(min_date, max_date, interval 1 day)) as full_date
            ) d
        """,
    ),
}