"""
RetailWise AI — ETL Result + Validation Models
Pydantic models for ETL pipeline outputs.
"""

from typing import List, Optional
from pydantic import BaseModel


class ValidationWarning(BaseModel):
    row_index: int
    field: str
    issue: str
    raw_value: Optional[str] = None


class ETLResult(BaseModel):
    shop_id: str
    entity: str             # "products" | "inventory" | "sales" | "suppliers"
    rows_extracted: int
    rows_transformed: int
    rows_inserted: int
    rows_updated: int
    rows_skipped: int
    rows_errored: int
    warnings: List[ValidationWarning] = []
    errors: List[str] = []
    duration_seconds: float
    success: bool

    @property
    def summary(self) -> str:
        return (
            f"[{self.shop_id}/{self.entity}] "
            f"extracted={self.rows_extracted} "
            f"inserted={self.rows_inserted} updated={self.rows_updated} "
            f"skipped={self.rows_skipped} errors={self.rows_errored} "
            f"({self.duration_seconds:.2f}s)"
        )


class ShopETLSummary(BaseModel):
    shop_id: str
    shop_name: str
    results: List[ETLResult]
    total_duration_seconds: float
    fully_successful: bool
