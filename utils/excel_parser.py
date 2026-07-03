import pandas as pd
from typing import Optional

from utils.logger import get_logger
from etl_config.bronze_config import BRONZE_CONFIG

logger = get_logger(__name__)


class ExcelSheetParser:
    """Parse Excel and map sheets to bronze tables based on column structure"""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        logger.info(f"Opening Excel file: {excel_path}")
        self.xls = pd.ExcelFile(excel_path)
        self.source_file_name = excel_path.split("/")[-1]
        logger.info(f"Found {len(self.xls.sheet_names)} sheet(s): {self.xls.sheet_names}")

    def _identify_table(self, columns: set) -> Optional[str]:
        """Find the table whose required columns are all present in the sheet"""
        matches = [
            name
            for name, cfg in BRONZE_CONFIG.items()
            if frozenset(cfg.required_columns).issubset(columns)
        ]

        if len(matches) == 0:
            return None
        if len(matches) > 1:
            logger.error(f"Ambiguous mapping for columns {columns}: matches {matches}")
            raise ValueError(
                f"Ambiguous mapping. Columns {columns} match multiple tables: {matches}"
            )
        return matches[0]

    def _schema_diagnostics(self, sheet_name: str, columns: set) -> str:
        """Which required column is missing for closest candidate schema"""
        diagnostics = []
        for name, cfg in BRONZE_CONFIG.items():
            required = frozenset(cfg.required_columns)
            missing_cols = required - columns
            if missing_cols and len(missing_cols) < len(required):
                diagnostics.append(
                    f"  - '{sheet_name}' is missing {missing_cols} to match '{name}'"
                )
        return "\n".join(diagnostics)

    def parse_all_sheets(self) -> dict:
        logger.info(f"Starting parse of {self.source_file_name}")
        discovered = {}
        unmatched_sheets = []
        diagnostics_log = []

        for sheet_name in self.xls.sheet_names:
            logger.debug(f"Reading sheet: {sheet_name}")
            df = pd.read_excel(self.xls, sheet_name=sheet_name)
            columns = set(df.columns)
            table_name = self._identify_table(columns)

            if table_name is None:
                logger.warning(f"Sheet '{sheet_name}' did not match any known schema")
                unmatched_sheets.append(sheet_name)
                diag = self._schema_diagnostics(sheet_name, columns)
                if diag:
                    diagnostics_log.append(diag)
                continue

            if table_name in discovered:
                logger.error(f"Duplicate mapping: '{sheet_name}' also maps to '{table_name}'")
                raise ValueError(
                    f"Duplicate - both {sheet_name} and previous sheet have {table_name} table name"
                )

            all_columns = set(BRONZE_CONFIG[table_name].all_columns)
            new_cols = columns - all_columns
            if new_cols:
                logger.warning(
                    f"Sheet '{sheet_name}' (table '{table_name}') has columns not in "
                    f"BRONZE_CONFIG.all_columns: {new_cols}. Consider adding them to the config."
                )

            logger.info(f"Sheet '{sheet_name}' -> table '{table_name}' ({len(df)} rows)")
            discovered[table_name] = df

        expected_names = set(BRONZE_CONFIG.keys())
        found_names = set(discovered.keys())
        missing = expected_names - found_names

        if missing:
            diagnostics_text = "\n".join(diagnostics_log)
            logger.error(f"Missing sheets for tables: {missing}")
            raise ValueError(
                f"Missing sheets for tables: {missing}\n"
                f"Sheets found without a matching schema: {unmatched_sheets}\n"
                f"{diagnostics_text}"
            )

        if unmatched_sheets:
            logger.warning(f"Sheets without a recognized schema (skipped): {unmatched_sheets}")

        logger.info(f"Parse complete. Discovered {len(discovered)} table(s): {list(discovered.keys())}")
        return discovered