from pyspark.sql.types import (
    StructType, StructField, DataType,
    StringType, IntegerType, DateType, TimestampType, DecimalType,
)

from etl_config.constants_config import ColumnDef

SILVER_TYPE_MAP: dict[str, DataType] = {
    "integer": IntegerType(),
    "string": StringType(),
    "date": DateType(),
    "timestamp": TimestampType(),
    "decimal(10,2)": DecimalType(10, 2),
    "decimal(10,4)": DecimalType(10, 4),
    "decimal(3,2)": DecimalType(3, 2),
}


def create_bronze_schema(required_cols: list[str]) -> StructType:
    """Bronze schema: string columns + audit columns."""
    fields = [StructField(col, StringType(), True) for col in required_cols]
    fields.extend([
        StructField("_source_file", StringType(), True),
        StructField("_ingested_at", TimestampType(), True),
        StructField("_batch_id", StringType(), True),
    ])
    return StructType(fields)


def get_spark_type(type_str: str) -> DataType:
    return SILVER_TYPE_MAP.get(type_str, StringType())


def create_silver_schema(cfg) -> StructType:
    """Silver schema: cast_columns/required_columns."""
    fields = [
        StructField(col_name, get_spark_type(col_type), col_name not in cfg.required_columns)
        for col_name, col_type in cfg.cast_columns.items()
    ]
    return StructType(fields)


def build_column_ddl(columns: list[ColumnDef]) -> str:
    """ Build SQL DDL for a list of columns"""
    lines = [
        f"{c.name} {c.sql_type}" + ("" if c.nullable else " not null")
        for c in columns
    ]
    return ",\n     ".join(lines)
