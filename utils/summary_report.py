from utils.logger import get_logger

logger = get_logger("summary_report")


def create_summary_report(
    spark,
    layer_name: str,
    tables: dict[str, dict],
    catalog: str,
    schema: str,
    batch_ids: list[str] | None = None,
) -> dict:
    
    summary = {}
    batch_filter = None
    if batch_ids:
        batch_filter = "'" + "','".join(batch_ids) + "'"

    for table_name, opts in tables.items():
        full_name = f"{catalog}.{schema}.{table_name}"
        df = spark.table(full_name)

        total_count = df.count()
        summary[f"{table_name}.total_count"] = total_count

        if batch_filter:
            this_run_count = df.filter(f"_batch_id IN ({batch_filter})").count()
            summary[f"{table_name}.this_run_count"] = this_run_count

        for col in opts.get("distinct_cols", []):
            summary[f"{table_name}.distinct_{col}"] = df.select(col).distinct().count()

    logger.info(f"=== {layer_name} Summary Report ===")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    logger.info("=" * (len(layer_name) + 20))

    return summary