"""
RetailWise AI — ETL End-to-End Test
Tests the full Extract → Transform → Load pipeline using Shop A's sample data.

Run from backend/ directory:
    python etl/test_etl.py

Or with the venv:
    .venv311\Scripts\python.exe etl/test_etl.py
"""

import os
import sys
import logging

# Ensure backend/ is on sys.path
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

os.chdir(_backend_dir)  # run from backend/ so relative paths resolve
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("etl.test")


def test_extract():
    logger.info("=" * 55)
    logger.info("TEST 1: Extractor")
    from etl.extractor import extract
    import yaml
    with open("shops/shop_a.yaml") as f:
        config = yaml.safe_load(f)
    source_cfg = config["sources"]["products"]
    df = extract(source_cfg, base_data_dir="data")
    assert len(df) > 0, "Should have extracted rows"
    assert "Item Code" in df.columns, "Should have raw column names"
    logger.info("✅ Extract: %d rows, columns=%s", len(df), list(df.columns))


def test_transform():
    logger.info("=" * 55)
    logger.info("TEST 2: Transformer")
    from etl.extractor import extract
    from etl.transformer import transform
    import yaml
    with open("shops/shop_a.yaml") as f:
        config = yaml.safe_load(f)
    source_cfg = config["sources"]["products"]
    raw_df = extract(source_cfg, base_data_dir="data")
    clean_df, warnings = transform(raw_df, "products", source_cfg, shop_id="shop_a")
    assert "name" in clean_df.columns, "Should have 'name' after transform"
    assert "sku" in clean_df.columns, "Should have 'sku' after transform"
    assert "selling_price" in clean_df.columns, "Should have 'selling_price'"
    assert clean_df["selling_price"].dtype == float, "selling_price should be float"
    assert all(c in ["staples", "dairy", "snacks", "spices", "beverages", "cleaning", "personal_care"]
               for c in clean_df["category"].values), "All categories should be valid"
    logger.info("✅ Transform: %d rows, columns=%s", len(clean_df), list(clean_df.columns))
    logger.info("   Sample:\n%s", clean_df[["sku", "name", "category", "selling_price"]].head(5).to_string())


def test_load_products():
    logger.info("=" * 55)
    logger.info("TEST 3: Load Products")
    from etl.pipeline import run_pipeline
    from database.db import SessionLocal
    from database.db import Base, engine
    from database.models import Product

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        before = db.query(Product).count()
        result = run_pipeline("shop_a", "products", db, on_conflict="skip")
        after = db.query(Product).count()
        logger.info("✅ Products: %s", result.summary)
        logger.info("   DB rows before=%d after=%d", before, after)
        assert result.rows_extracted > 0
        # Either inserted or skipped (if already exists)
        assert result.rows_inserted + result.rows_skipped == result.rows_extracted - result.rows_errored
    finally:
        db.close()


def test_load_suppliers():
    logger.info("=" * 55)
    logger.info("TEST 4: Load Suppliers")
    from etl.pipeline import run_pipeline
    from database.db import SessionLocal
    from database.models import Supplier
    db = SessionLocal()
    try:
        result = run_pipeline("shop_a", "suppliers", db, on_conflict="skip")
        count = db.query(Supplier).count()
        logger.info("✅ Suppliers: %s | DB total=%d", result.summary, count)
        assert result.rows_extracted > 0
    finally:
        db.close()


def test_load_inventory():
    logger.info("=" * 55)
    logger.info("TEST 5: Load Inventory")
    from etl.pipeline import run_pipeline
    from database.db import SessionLocal
    from database.models import InventoryBatch
    db = SessionLocal()
    try:
        result = run_pipeline("shop_a", "inventory", db, on_conflict="update")
        count = db.query(InventoryBatch).count()
        logger.info("✅ Inventory: %s | DB total=%d", result.summary, count)
        assert result.rows_extracted > 0
    finally:
        db.close()


def test_load_sales():
    logger.info("=" * 55)
    logger.info("TEST 6: Load Sales")
    from etl.pipeline import run_pipeline
    from database.db import SessionLocal
    from database.models import SalesRecord
    db = SessionLocal()
    try:
        result = run_pipeline("shop_a", "sales", db, on_conflict="skip")
        count = db.query(SalesRecord).count()
        logger.info("✅ Sales: %s | DB total=%d", result.summary, count)
    finally:
        db.close()


def test_full_pipeline():
    logger.info("=" * 55)
    logger.info("TEST 7: Full Pipeline (all entities)")
    from etl.pipeline import run_shop_pipeline
    from database.db import SessionLocal
    db = SessionLocal()
    try:
        summary = run_shop_pipeline("shop_a", db, on_conflict="skip")
        logger.info("✅ Full pipeline: %d entities run in %.2fs",
                    len(summary.results), summary.total_duration_seconds)
        for r in summary.results:
            logger.info("   %s", r.summary)
    finally:
        db.close()


def test_list_shops():
    logger.info("=" * 55)
    logger.info("TEST 8: List Shops")
    from etl.pipeline import list_shops
    shops = list_shops()
    logger.info("✅ Found %d shops: %s", len(shops), [s["shop_id"] for s in shops])
    assert len(shops) >= 1


if __name__ == "__main__":
    tests = [
        test_extract,
        test_transform,
        test_load_products,
        test_load_suppliers,
        test_load_inventory,
        test_load_sales,
        test_full_pipeline,
        test_list_shops,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as exc:
            logger.error("❌ %s FAILED: %s", test_fn.__name__, exc)
            failed += 1

    logger.info("=" * 55)
    logger.info("Results: %d passed, %d failed", passed, failed)
    sys.exit(0 if failed == 0 else 1)
