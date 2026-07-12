from dataclasses import dataclass

CATALOG = "acme_catalog"

LANDING_SCHEMA = "landing"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

LANDING = f"{CATALOG}.{LANDING_SCHEMA}"
BRONZE = f"{CATALOG}.{BRONZE_SCHEMA}"
SILVER = f"{CATALOG}.{SILVER_SCHEMA}"
GOLD = f"{CATALOG}.{GOLD_SCHEMA}"

LANDING_DIR = f"/Volumes/{CATALOG}/{LANDING_SCHEMA}/raw_files"
PROCESSED_DIR = f"{LANDING_DIR}/processed"
FAILED_DIR = f"{LANDING_DIR}/failed"

WATERMARK_TABLE = f"{SILVER}._watermark"
QUARANTINE_TABLE = f"{SILVER}._quarantine"


@dataclass
class ColumnDef:
    """Single column definition: name, SQL type, nullability, and comment."""
    name: str
    sql_type: str
    nullable: bool = True
    comment: str = ""

