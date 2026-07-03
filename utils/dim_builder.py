from pyspark.sql.functions import col, current_timestamp, lit, monotonically_increasing_id, year, quarter, month, dayofmonth, dayofweek, weekofyear, date_format
from delta.tables import DeltaTable

def _build_source_dataframe(spark, catalog: str, source_schema: str, config: dict):
    """Denormalization of source DataFrame for a dimension"""

    df = spark.table(f"{catalog}.{source_schema}.{config['source']}")

    for join_table, join_key, join_type in config["joins"]:
        right_df = spark.table(f"{catalog}.{source_schema}.{join_table}")
        df = df.join(right_df, on=join_key, how=join_type)

    return df.select(*config["columns"])

def build_scd1_dimension(spark, catalog: str, source_schema: str, target_schema: str, dim_name: str, config: dict):
    """SCD1 - full overwrite, no history tracking"""
    df = _build_source_dataframe(spark, catalog, source_schema, config)
    df = df.withColumn("_gold_loaded_at", current_timestamp())

    full_table_name = f"{catalog}.{target_schema}.{dim_name}"
    (
        df.write
          .format("delta")
          .mode("overwrite")
          .option("overwriteSchema", "true")
          .saveAsTable(full_table_name)
    )

    row_count = df.count()
    print(f"OK (SCD1): {full_table_name} -> {row_count} rows")
    return row_count

def build_scd2_dimension(spark, catalog: str, source_schema: str, target_schema: str, dim_name: str, config: dict):
    """SCD2 - merge new records, keep history"""
    business_key = config["business_key"]
    tracked_columns = config["tracked_columns"]
    full_table_name = f"{catalog}.{target_schema}.{dim_name}"

    source_df = _build_source_dataframe(spark, catalog, source_schema, config)

    table_exists = spark.catalog.tableExists(full_table_name)
    
    if not table_exists:
        df = (
            source_df
              .withColumn(f"{dim_name}_SK", mononically_increasing_id())
              .withColumn(f"valid_from", current_timestamp())
              .withColumn(f"valid_to", lit(None).cast("timestamp"))
              .withColumn("is_current", lit(True))
              .withColumn("_gold_loaded_at", current_timestamp())
        )
        (
            df.write
              .format("delta")
              .mode("overwrite")
              .option("overwriteSchema", "true")
              .saveAsTable(full_table_name)
        )
        row_count = df.count()
        print(f"OK (SCD2): {full_table_name} -> {row_count} rows")
        return row_count
    
    