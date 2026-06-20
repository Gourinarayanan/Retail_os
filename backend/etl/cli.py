"""
RetailWise AI — ETL CLI
Run ETL pipelines from the terminal without starting the FastAPI server.

Usage:
    # Load all entities for shop_a (from backend/)
    python -m etl.cli --shop shop_a

    # Load only products for shop_b
    python -m etl.cli --shop shop_b --entity products

    # Load with update-on-conflict instead of skip
    python -m etl.cli --shop shop_a --on-conflict update

    # List all configured shops
    python -m etl.cli --list-shops
"""

import argparse
import logging
import sys
import os

# ── Ensure backend/ is on sys.path so imports work ────────────────────────────
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("etl.cli")


def main():
    parser = argparse.ArgumentParser(
        description="RetailWise AI — ETL CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--shop",
        metavar="SHOP_ID",
        help="Shop ID to run ETL for (must match a file in shops/<shop_id>.yaml)",
    )
    parser.add_argument(
        "--entity",
        metavar="ENTITY",
        choices=["products", "inventory", "sales", "suppliers"],
        help="Specific entity to load (default: all entities in dependency order)",
    )
    parser.add_argument(
        "--on-conflict",
        dest="on_conflict",
        choices=["skip", "update"],
        default="skip",
        help="How to handle existing records: skip (default) or update",
    )
    parser.add_argument(
        "--list-shops",
        action="store_true",
        help="List all configured shops and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run extract + transform but skip the load step (validates data only)",
    )

    args = parser.parse_args()

    from etl.pipeline import list_shops, run_pipeline, run_shop_pipeline

    # ── List shops ────────────────────────────────────────────────────────────
    if args.list_shops:
        shops = list_shops()
        if not shops:
            print("No shops configured. Add a YAML file to the shops/ directory.")
            return
        print(f"\n{'Shop ID':<20} {'Shop Name':<30} {'Location':<25} {'Entities'}")
        print("-" * 90)
        for s in shops:
            print(
                f"{s['shop_id']:<20} {s['shop_name']:<30} {s['location']:<25} "
                f"{', '.join(s['entities'])}"
            )
        print()
        return

    if not args.shop:
        parser.error("--shop is required unless --list-shops is specified")

    # ── Dry run ───────────────────────────────────────────────────────────────
    if args.dry_run:
        _dry_run(args.shop, args.entity)
        return

    # ── Real ETL run ──────────────────────────────────────────────────────────
    from database.db import SessionLocal
    db = SessionLocal()

    try:
        if args.entity:
            result = run_pipeline(args.shop, args.entity, db, on_conflict=args.on_conflict)
            _print_result(result)
            sys.exit(0 if result.success else 1)
        else:
            summary = run_shop_pipeline(args.shop, db, on_conflict=args.on_conflict)
            _print_summary(summary)
            sys.exit(0 if summary.fully_successful else 1)
    finally:
        db.close()


def _dry_run(shop_id: str, entity: str | None):
    """Extract + transform only. Shows what would be loaded without touching the DB."""
    import yaml
    from pathlib import Path
    from etl.extractor import extract
    from etl.transformer import transform
    from etl.pipeline import SHOPS_DIR, DATA_DIR

    config_path = Path(SHOPS_DIR) / f"{shop_id}.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    entities = [entity] if entity else list(config.get("sources", {}).keys())

    for ent in entities:
        source_cfg = config["sources"].get(ent)
        if not source_cfg:
            print(f"[dry-run] No source configured for entity '{ent}'")
            continue

        print(f"\n{'=' * 60}")
        print(f"[dry-run] {shop_id}/{ent}")
        print(f"{'=' * 60}")

        raw_df = extract(source_cfg, base_data_dir=DATA_DIR)
        print(f"Extracted {len(raw_df)} rows. Columns: {list(raw_df.columns)}")

        clean_df, warnings = transform(raw_df, ent, source_cfg, shop_id=shop_id)
        print(f"Transformed → {len(clean_df)} rows. Columns: {list(clean_df.columns)}")

        if warnings:
            print(f"\n⚠️  {len(warnings)} validation warnings:")
            for w in warnings[:10]:
                print(f"  Row {w.row_index} | {w.field}: {w.issue}")

        print(f"\nSample (first 3 rows):")
        print(clean_df.head(3).to_string())


def _print_result(result):
    status = "✅" if result.success else "❌"
    print(f"\n{status} {result.shop_id}/{result.entity}")
    print(f"   Extracted : {result.rows_extracted}")
    print(f"   Inserted  : {result.rows_inserted}")
    print(f"   Updated   : {result.rows_updated}")
    print(f"   Skipped   : {result.rows_skipped}")
    print(f"   Errors    : {result.rows_errored}")
    print(f"   Duration  : {result.duration_seconds}s")
    if result.errors:
        print(f"\n   Errors:")
        for e in result.errors:
            print(f"     • {e}")


def _print_summary(summary):
    status = "✅" if summary.fully_successful else "⚠️"
    print(f"\n{status} Full ETL for '{summary.shop_name}' ({summary.shop_id})")
    print(f"   Total duration: {summary.total_duration_seconds}s\n")
    for r in summary.results:
        _print_result(r)


if __name__ == "__main__":
    main()
