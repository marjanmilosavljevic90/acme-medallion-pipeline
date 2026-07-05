# ACME Medallion Pipeline

A Databricks Lakehouse ETL pipeline that ingests ACME sale data from Excel exports and builds a medallion architecture:

### BRONZE -> SILVER -> GOLD

### Bronze:

- raw append-only tables, 
- 1:1 with source sheets, 
- flagged with _source_file / _ingested_at / _batch_id
- After excel data is processed by run_bronze, file is moved to processed if successfull, if not in failed
- run_bronze can handle format/structure changes in excel file

### Silver:

- cleaned & typed tables: column rename, type casts, required-column
- validation, deduplication, 
- MERGE upsert, 
- watermark-based incremental processing, 
- bad rows routed to quarantine

### Gold:

- star schema: 
    - SCD2 dimensions (customers, products, shippers)
    - static dimensions (division, date)
    - fact tables (orders, order_lines, shipments)

Catalog/schema layout (Unity Catalog): `acme_catalog.{landing, bronze, silver, gold}`

## How a run works

1. **Bronze** (`01_run_bronze.ipynb`): scans the landing volume for `.xlsx` files, parses every
   sheet with `ExcelSheetParser` (which identifies the target table by checking which table's
   `required_columns` are a subset of the sheet's columns), appends to the matching Bronze Delta
   table, and moves the source file to `processed/` (or `failed/` if any sheet in the file errors).
2. **Silver** (`02_set_silver_tables.ipynb` + `03_run_silver.ipynb`): for each configured table,
   reads Bronze rows ingested since the last successful watermark, renames columns to snake_case,
   casts to the target types, quarantines rows with missing required values or failed casts,
   deduplicates on the table's key columns, and `MERGE`s the result into Silver. Watermark and
   quarantine tables live at `acme_catalog.silver._watermark` / `_quarantine`.
3. **Gold dimensions** (`04_set_gold_dims.ipynb` + `05_run_gold_dims.ipynb`): tables with
   `tracked_columns` configured (`dim_customers`, `dim_products`, `dim_shippers`) get full SCD2
   treatment — expire changed rows, insert new versions, insert brand-new natural keys. Tables
   without tracked columns (`dim_division`, `dim_date`) get a plain SCD1 upsert.
4. **Gold facts** (`06_set_gold_facts.ipynb` + `07_run_gold_facts.ipynb`): each fact is a single
   `MERGE` driven by the config's `source_query`, joining Silver against the current (`is_current = true`) rows of the relevant Gold dimensions to resolve surrogate keys.

## Adding a new table

Because everything is config-driven, most changes don't touch notebook code:

- **New Bronze source** → add an entry to `BRONZE_CONFIG` in `etl_config/bronze_config.py`.
- **New Silver table** → add an entry to `SILVER_CONFIG` in `etl_config/silver_config.py`, then
  re-run `setup/02_setup_silver.ipynb` to create the table.
- **New Gold dimension/fact** → add an entry to `DIM_CONFIG` / `FACT_CONFIG`, re-run the matching
  `setup/03_*` or `setup/04_*` notebook, then it's automatically picked up by the `set_*` fan-out
  notebook on the next pipeline run.