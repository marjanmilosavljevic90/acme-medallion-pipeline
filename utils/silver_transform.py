from pyspark.sql import DataFrame
from pyspark.sql.functions import array, array_compact, col, current_timestamp, lit, struct, to_json, when

from etl_config.constants_config import QUARANTINE_TABLE
from utils.logger import get_logger

logger = get_logger("silver_transform")


def get_missing_required(df: DataFrame, required_columns: list[str]) -> DataFrame:
    return df.withColumn(
        "_missing_columns",
        array_compact(
            array(*[when(col(c).isNull(), lit(c)) for c in required_columns])
        ),
    )


def to_quarantine(df: DataFrame, table_name: str, error_type: str) -> None:
    row_count = df.count()
    if row_count == 0:
        return

    quarantine_df = df.select(
        lit(table_name).alias("table_name"),
        col("_batch_id").alias("batch_id"),
        current_timestamp().alias("rejected_at"),
        lit(error_type).alias("error_type"),
        col("_missing_columns"),
        to_json(
            struct(*[
                c for c in df.columns
                if c not in ("_missing_columns", "_batch_id", "_ingested_at")
            ])
        ).alias("raw_data"),
    )

    quarantine_df.write.format("delta").mode("append").saveAsTable(QUARANTINE_TABLE)
    logger.warning(f"'{table_name}': {row_count} rows quarantined as {error_type}")
