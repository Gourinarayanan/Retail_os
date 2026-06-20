"""
RetailWise AI — ETL Extractor
Reads raw source files (CSV, Excel, JSON) into a Pandas DataFrame.
The extractor is source-agnostic: all it does is read the file into memory.
"""

import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Supported formats
SUPPORTED_FORMATS = {"csv", "excel", "xlsx", "xls", "json"}


def extract(source_config: dict, base_data_dir: str = "data") -> pd.DataFrame:
    """
    Read a raw data file into a DataFrame.

    Args:
        source_config: The source block from the shop YAML config, e.g.:
            {
                "file": "data/shop_a/items_master.csv",
                "format": "csv",
                "sheet": "Sheet1",       # Excel only
                "encoding": "utf-8",     # CSV only, optional
            }
        base_data_dir: Root directory for data files (relative to backend/).

    Returns:
        A Pandas DataFrame with raw, unmodified column names.

    Raises:
        FileNotFoundError: If the source file does not exist.
        ValueError: If the file format is unsupported.
    """
    file_path = Path(source_config["file"])

    if not file_path.is_absolute():
        file_path = Path(base_data_dir) / file_path

    if not file_path.exists():
        raise FileNotFoundError(f"ETL source file not found: {file_path.resolve()}")

    fmt = source_config.get("format", _infer_format(file_path)).lower()

    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported file format '{fmt}'. Supported: {SUPPORTED_FORMATS}"
        )

    logger.info("[extract] Reading %s as format='%s'", file_path, fmt)

    if fmt == "csv":
        encoding = source_config.get("encoding", "utf-8-sig")
        delimiter = source_config.get("delimiter", ",")
        df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, dtype=str)

    elif fmt in {"excel", "xlsx", "xls"}:
        sheet = source_config.get("sheet", 0)
        df = pd.read_excel(file_path, sheet_name=sheet, dtype=str)

    elif fmt == "json":
        orient = source_config.get("orient", None)
        with open(file_path, encoding="utf-8") as f:
            raw = json.load(f)

        # Support both list-of-dicts (records) and dict-of-lists (columns) JSON
        if isinstance(raw, list):
            df = pd.DataFrame(raw)
        elif isinstance(raw, dict):
            # Could be {"data": [...]} wrapper or actual column dict
            list_keys = [k for k, v in raw.items() if isinstance(v, list)]
            if len(list_keys) == 1:
                df = pd.DataFrame(raw[list_keys[0]])
            else:
                df = pd.DataFrame(raw)
        else:
            raise ValueError("JSON file must contain a list or a dict of records.")

        df = df.astype(str)

    # Strip whitespace from all string columns
    df = df.apply(lambda col: col.str.strip() if col.dtype == object else col)

    # Drop fully-empty rows
    df = df.dropna(how="all")

    logger.info("[extract] Loaded %d rows, %d columns from %s", len(df), len(df.columns), file_path.name)
    return df


def _infer_format(path: Path) -> str:
    """Infer file format from file extension."""
    suffix = path.suffix.lower().lstrip(".")
    if suffix in {"xlsx", "xls"}:
        return "excel"
    return suffix  # "csv", "json", etc.
