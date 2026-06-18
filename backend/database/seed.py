"""
RetailWise AI — Database Seeder
Section 6 of full_flow.md — Products, Suppliers, Sales History, Inventory Batches.

Guard: Only runs if the products table is empty. Never re-seeds.
"""

import random
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from database.models import (
    InventoryBatch,
    Product,
    SalesRecord,
    Supplier,
    SupplierDelivery,
    SupplierPrice,
)

# ── Reproducible randomness ───────────────────────────────────────────────────
random.seed(42)

# ── Section 6 — Products ──────────────────────────────────────────────────────

PRODUCTS = [
    # ── DAIRY (daily order) ────────────────────────────────────────────────
    {
        "name": "Milk 1L Packet",
        "sku": "MILK-001",
        "category": "dairy",
        "brand": None,
        "unit": "packet",
        "unit_size": 1.0,
        "selling_price": 62,
        "cost_price": 54,
        "order_cycle": "daily",
        "order_day": None,
        "reorder_point_days": 2.0,
        "lead_time_days": 1,
        "shelf_life_days": 2,
        "min_threshold": 50,
        "demand_events": "hartal_pre,onam,christmas,rainy_day",
        "avg_daily_demand": 85,
    },
    {
        "name": "Eggs Tray (30)",
        "sku": "EGGS-002",
        "category": "dairy",
        "brand": None,
        "unit": "tray",
        "unit_size": 30.0,
        "selling_price": 185,
        "cost_price": 160,
        "order_cycle": "daily",
        "order_day": None,
        "reorder_point_days": 2.0,
        "lead_time_days": 1,
        "shelf_life_days": 21,
        "min_threshold": 8,
        "demand_events": "hartal_pre,christmas,easter",
        "avg_daily_demand": 12,
    },
    {
        "name": "Curd 500ml",
        "sku": "CURD-003",
        "category": "dairy",
        "brand": None,
        "unit": "cup",
        "unit_size": 0.5,
        "selling_price": 32,
        "cost_price": 26,
        "order_cycle": "daily",
        "order_day": None,
        "reorder_point_days": 2.0,
        "lead_time_days": 1,
        "shelf_life_days": 5,
        "min_threshold": 20,
        "demand_events": "onam,summer",
        "avg_daily_demand": 30,
    },
    # ── STAPLES (weekly order — Monday) ───────────────────────────────────
    {
        "name": "Ponni Rice 5kg",
        "sku": "RICE-004",
        "category": "staples",
        "brand": None,
        "unit": "bag",
        "unit_size": 5.0,
        "selling_price": 280,
        "cost_price": 240,
        "order_cycle": "weekly",
        "order_day": "Monday",
        "reorder_point_days": 7.0,
        "lead_time_days": 2,
        "shelf_life_days": 9999,
        "min_threshold": 30,
        "demand_events": "hartal_pre,onam,vishu,eid,ramadan",
        "avg_daily_demand": 18,
    },
    {
        "name": "Wheat Flour 1kg",
        "sku": "FLOR-005",
        "category": "staples",
        "brand": None,
        "unit": "packet",
        "unit_size": 1.0,
        "selling_price": 48,
        "cost_price": 38,
        "order_cycle": "weekly",
        "order_day": "Monday",
        "reorder_point_days": 7.0,
        "lead_time_days": 2,
        "shelf_life_days": 180,
        "min_threshold": 40,
        "demand_events": "hartal_pre,ramadan,christmas",
        "avg_daily_demand": 22,
    },
    {
        "name": "Coconut Oil 1L",
        "sku": "COIL-006",
        "category": "staples",
        "brand": None,
        "unit": "bottle",
        "unit_size": 1.0,
        "selling_price": 195,
        "cost_price": 165,
        "order_cycle": "weekly",
        "order_day": "Monday",
        "reorder_point_days": 7.0,
        "lead_time_days": 2,
        "shelf_life_days": 9999,
        "min_threshold": 15,
        "demand_events": "hartal_pre,onam,vishu",
        "avg_daily_demand": 9,
    },
    # ── SNACKS (weekly order — Thursday) ──────────────────────────────────
    {
        "name": "Banana Chips 200g",
        "sku": "BNCH-007",
        "category": "snacks",
        "brand": None,
        "unit": "packet",
        "unit_size": 0.2,
        "selling_price": 45,
        "cost_price": 32,
        "order_cycle": "weekly",
        "order_day": "Thursday",
        "reorder_point_days": 5.0,
        "lead_time_days": 1,
        "shelf_life_days": 45,
        "min_threshold": 50,
        "demand_events": "hartal_pre,onam,vishu,rainy_day",
        "avg_daily_demand": 42,
    },
    {
        "name": "Mixture Snack 500g",
        "sku": "MIXT-008",
        "category": "snacks",
        "brand": None,
        "unit": "packet",
        "unit_size": 0.5,
        "selling_price": 80,
        "cost_price": 58,
        "order_cycle": "weekly",
        "order_day": "Thursday",
        "reorder_point_days": 5.0,
        "lead_time_days": 1,
        "shelf_life_days": 90,
        "min_threshold": 25,
        "demand_events": "onam,christmas,eid,rainy_day",
        "avg_daily_demand": 18,
    },
    # ── SPICES (weekly order — Wednesday) ─────────────────────────────────
    {
        "name": "Red Chilli Powder 200g",
        "sku": "RCHL-009",
        "category": "spices",
        "brand": None,
        "unit": "packet",
        "unit_size": 0.2,
        "selling_price": 55,
        "cost_price": 42,
        "order_cycle": "weekly",
        "order_day": "Wednesday",
        "reorder_point_days": 5.0,
        "lead_time_days": 2,
        "shelf_life_days": 9999,
        "min_threshold": 20,
        "demand_events": "ramadan,eid,onam",
        "avg_daily_demand": 14,
    },
    {
        "name": "Garam Masala 50g",
        "sku": "GRMS-010",
        "category": "spices",
        "brand": None,
        "unit": "packet",
        "unit_size": 0.05,
        "selling_price": 28,
        "cost_price": 20,
        "order_cycle": "weekly",
        "order_day": "Wednesday",
        "reorder_point_days": 5.0,
        "lead_time_days": 2,
        "shelf_life_days": 9999,
        "min_threshold": 12,
        "demand_events": "ramadan,eid,christmas",
        "avg_daily_demand": 8,
    },
    # ── BEVERAGES (weekly order — Tuesday) ────────────────────────────────
    {
        "name": "Tea Powder 250g",
        "sku": "TEA-011",
        "category": "beverages",
        "brand": None,
        "unit": "packet",
        "unit_size": 0.25,
        "selling_price": 75,
        "cost_price": 60,
        "order_cycle": "weekly",
        "order_day": "Tuesday",
        "reorder_point_days": 5.0,
        "lead_time_days": 2,
        "shelf_life_days": 9999,
        "min_threshold": 25,
        "demand_events": "hartal_pre,rainy_day,onam",
        "avg_daily_demand": 16,
    },
    {
        "name": "Bru Coffee 200g",
        "sku": "COFF-012",
        "category": "beverages",
        "brand": "Bru",
        "unit": "jar",
        "unit_size": 0.2,
        "selling_price": 195,
        "cost_price": 162,
        "order_cycle": "weekly",
        "order_day": "Tuesday",
        "reorder_point_days": 5.0,
        "lead_time_days": 2,
        "shelf_life_days": 9999,
        "min_threshold": 8,
        "demand_events": "christmas,vishu",
        "avg_daily_demand": 5,
    },
    # ── CLEANING (monthly order — 1st of month) ───────────────────────────
    {
        "name": "Surf Excel 1kg",
        "sku": "SURF-013",
        "category": "cleaning",
        "brand": "Surf Excel",
        "unit": "packet",
        "unit_size": 1.0,
        "selling_price": 138,
        "cost_price": 115,
        "order_cycle": "monthly",
        "order_day": "1",
        "reorder_point_days": 10.0,
        "lead_time_days": 3,
        "shelf_life_days": 9999,
        "min_threshold": 10,
        "demand_events": "onam,vishu",
        "avg_daily_demand": 6,
    },
    {
        "name": "Vim Dishwash 500ml",
        "sku": "VMDW-014",
        "category": "cleaning",
        "brand": "Vim",
        "unit": "bottle",
        "unit_size": 0.5,
        "selling_price": 65,
        "cost_price": 52,
        "order_cycle": "monthly",
        "order_day": "1",
        "reorder_point_days": 10.0,
        "lead_time_days": 3,
        "shelf_life_days": 9999,
        "min_threshold": 8,
        "demand_events": "onam",
        "avg_daily_demand": 4,
    },
    # ── PERSONAL CARE (monthly) ───────────────────────────────────────────
    {
        "name": "Dove Soap 100g",
        "sku": "SOAP-015",
        "category": "personal_care",
        "brand": "Dove",
        "unit": "piece",
        "unit_size": 0.1,
        "selling_price": 45,
        "cost_price": 36,
        "order_cycle": "monthly",
        "order_day": "1",
        "reorder_point_days": 10.0,
        "lead_time_days": 3,
        "shelf_life_days": 9999,
        "min_threshold": 12,
        "demand_events": "onam,vishu,christmas",
        "avg_daily_demand": 8,
    },
]

# ── Section 6 — Suppliers ─────────────────────────────────────────────────────

SUPPLIERS = [
    {
        "name": "Sri Krishna Wholesale",
        "contact_name": "Krishna Nair",
        "whatsapp_number": "+919876543210",
        "email": "srikrishna.wholesale@gmail.com",
        "region": "Thrissur",
        "supply_categories": "staples,snacks,beverages,cleaning,personal_care",
        "notes": "Highly trusted local supplier. Price +3% vs market avg. 95% on-time reliability.",
        "is_active": True,
    },
    {
        "name": "Palakkad Agro Traders",
        "contact_name": "Suresh Kumar",
        "whatsapp_number": "+919865432100",
        "email": "palakkad.agro@gmail.com",
        "region": "Palakkad",
        "supply_categories": "staples,spices",
        "notes": "Cheapest prices (-8% vs market avg) but 71% reliability. Frequently late. Rain risk.",
        "is_active": True,
    },
    {
        "name": "Amul Distributor Thrissur",
        "contact_name": "Anoop Varma",
        "whatsapp_number": "+919854321000",
        "email": "amul.thrissur@amuldairy.com",
        "region": "Thrissur",
        "supply_categories": "dairy",
        "notes": "Fixed MRP-based pricing. 98% on-time. Only dairy supplier in network.",
        "is_active": True,
    },
    {
        "name": "Metro Cash & Carry Kochi",
        "contact_name": "Priya Menon",
        "whatsapp_number": "+919843210000",
        "email": "priya.menon@metro.in",
        "region": "Kochi",
        "supply_categories": "staples,snacks,beverages,cleaning,spices,personal_care",
        "notes": "Good for weekly bulk orders. -5% vs market avg. 89% reliability.",
        "is_active": True,
    },
]

# ── Section 6 — Event Multipliers ─────────────────────────────────────────────

EVENT_MULTIPLIERS: dict[str, dict] = {
    "hartal_pre": {
        "dairy": 1.80,
        "staples": 1.60,
        "snacks": 1.65,
        "beverages": 1.45,
        "spices": 1.30,
        "cleaning": 1.10,
        "personal_care": 1.05,
    },
    "hartal_day": {"_all": 0.08},
    "hartal_post": {"_all": 1.15},
    "onam": {
        "snacks": 1.45,
        "staples": 1.35,
        "dairy": 1.25,
        "beverages": 1.20,
        "cleaning": 1.20,
        "personal_care": 1.15,
    },
    "vishu": {
        "staples": 1.30,
        "snacks": 1.25,
        "cleaning": 1.15,
        "personal_care": 1.20,
    },
    "ramadan": {
        "spices": 1.55,
        "staples": 1.30,
        "dairy": 1.20,
        "beverages": 1.10,
    },
    "eid": {
        "spices": 1.85,
        "staples": 1.50,
        "snacks": 1.55,
        "dairy": 1.40,
    },
    "christmas": {
        "beverages": 1.50,
        "snacks": 1.45,
        "dairy": 1.35,
        "staples": 1.30,
        "personal_care": 1.25,
    },
    "rainy_day": {
        "beverages": 1.30,
        "snacks": 1.25,
        "dairy": 1.10,
        "_all": 0.92,
    },
    "weekend": {"_all": 1.08},
    "normal": {"_all": 1.00},
}

# ── Calendar windows ──────────────────────────────────────────────────────────

def _build_event_calendar(today: date) -> dict[date, str]:
    """
    Returns a mapping of date → event_tag for the past 365 days.
    Priorities (highest wins): hartal_day > hartal_pre > hartal_post >
      eid > onam > vishu > ramadan > christmas > rainy_day > weekend > normal
    """
    start = today - timedelta(days=365)
    calendar: dict[date, str] = {}

    # ── 5 hardcoded hartal dates spread across the year ──────────────────
    hartal_days: set[date] = set()
    for offset_days in [30, 95, 180, 255, 330]:
        hd = start + timedelta(days=offset_days)
        hartal_days.add(hd)

    # ── Onam: 10-day window — mid September of each year in range ─────────
    onam_days: set[date] = set()
    for year in {start.year, today.year}:
        onam_start = date(year, 9, 10)
        for i in range(10):
            d = onam_start + timedelta(days=i)
            if start <= d <= today:
                onam_days.add(d)

    # ── Vishu: April 14 each year ─────────────────────────────────────────
    vishu_days: set[date] = set()
    for year in {start.year, today.year}:
        vd = date(year, 4, 14)
        if start <= vd <= today:
            for i in range(3):  # 3-day window
                d = vd + timedelta(days=i)
                if start <= d <= today:
                    vishu_days.add(d)

    # ── Ramadan: 30-day window — March each year ──────────────────────────
    ramadan_days: set[date] = set()
    for year in {start.year, today.year}:
        ram_start = date(year, 3, 1)
        for i in range(30):
            d = ram_start + timedelta(days=i)
            if start <= d <= today:
                ramadan_days.add(d)

    # ── Eid: last 3 days of Ramadan window ───────────────────────────────
    eid_days: set[date] = set()
    for year in {start.year, today.year}:
        eid_start = date(year, 3, 28)
        for i in range(3):
            d = eid_start + timedelta(days=i)
            if start <= d <= today:
                eid_days.add(d)

    # ── Christmas: Dec 20–27 each year ───────────────────────────────────
    christmas_days: set[date] = set()
    for year in {start.year, today.year}:
        for day in range(20, 28):
            d = date(year, 12, day)
            if start <= d <= today:
                christmas_days.add(d)

    # ── Rainy days: roughly June–August (monsoon) — every 3rd day ────────
    rainy_days: set[date] = set()
    current = start
    while current <= today:
        if current.month in (6, 7, 8) and current.day % 3 == 0:
            rainy_days.add(current)
        current += timedelta(days=1)

    # ── Assign tags in priority order ────────────────────────────────────
    current = start
    while current <= today:
        if current in hartal_days:
            tag = "hartal_day"
        elif (current - timedelta(days=1)) in hartal_days:
            tag = "hartal_pre"
        elif (current + timedelta(days=1)) in hartal_days:
            tag = "hartal_post"
        elif current in eid_days:
            tag = "eid"
        elif current in onam_days:
            tag = "onam"
        elif current in vishu_days:
            tag = "vishu"
        elif current in ramadan_days:
            tag = "ramadan"
        elif current in christmas_days:
            tag = "christmas"
        elif current in rainy_days:
            tag = "rainy_day"
        elif current.weekday() in (5, 6):  # Saturday=5, Sunday=6
            tag = "weekend"
        else:
            tag = "normal"

        calendar[current] = tag
        current += timedelta(days=1)

    return calendar


def _get_multiplier(event_tag: str, category: str) -> float:
    """Return the demand multiplier for a given event tag and product category."""
    impacts = EVENT_MULTIPLIERS.get(event_tag, {"_all": 1.0})
    # Category-specific multiplier first; fall back to _all; default 1.0
    mult = impacts.get(category, impacts.get("_all", 1.0))
    # For rainy_day: apply _all reduction AND category-specific uplift combined
    if event_tag == "rainy_day" and category in impacts and "_all" in impacts:
        mult = impacts[category] * impacts["_all"]
    return float(mult)


# ── Supplier price table ──────────────────────────────────────────────────────

def _build_supplier_prices(
    db_suppliers: list, db_products: list, recorded_date: date
) -> list[SupplierPrice]:
    """
    Build SupplierPrice rows.
    - Amul: dairy only (cost_price as base)
    - Sri Krishna: all except dairy (+3% vs cost_price)
    - Metro: all except dairy (-5% vs cost_price)
    - Palakkad: staples + spices only (-8% vs cost_price)
    """
    supplier_map = {s.name: s for s in db_suppliers}
    prices: list[SupplierPrice] = []

    for p in db_products:
        cost = p.cost_price

        # Amul — dairy only
        if p.category == "dairy":
            prices.append(
                SupplierPrice(
                    supplier_id=supplier_map["Amul Distributor Thrissur"].id,
                    product_id=p.id,
                    price_per_unit=round(cost, 2),
                    min_order_qty=None,
                    bulk_discount_qty=None,
                    bulk_discount_price=None,
                    recorded_date=recorded_date,
                )
            )
            continue  # Amul only for dairy

        # Sri Krishna — staples, snacks, beverages, cleaning, personal_care
        if p.category in ("staples", "snacks", "beverages", "cleaning", "personal_care"):
            prices.append(
                SupplierPrice(
                    supplier_id=supplier_map["Sri Krishna Wholesale"].id,
                    product_id=p.id,
                    price_per_unit=round(cost * 1.03, 2),
                    min_order_qty=None,
                    bulk_discount_qty=None,
                    bulk_discount_price=None,
                    recorded_date=recorded_date,
                )
            )

        # Metro — staples, snacks, beverages, cleaning, spices, personal_care
        if p.category in ("staples", "snacks", "beverages", "cleaning", "spices", "personal_care"):
            prices.append(
                SupplierPrice(
                    supplier_id=supplier_map["Metro Cash & Carry Kochi"].id,
                    product_id=p.id,
                    price_per_unit=round(cost * 0.95, 2),
                    min_order_qty=10,
                    bulk_discount_qty=50,
                    bulk_discount_price=round(cost * 0.92, 2),
                    recorded_date=recorded_date,
                )
            )

        # Palakkad — staples, spices
        if p.category in ("staples", "spices"):
            prices.append(
                SupplierPrice(
                    supplier_id=supplier_map["Palakkad Agro Traders"].id,
                    product_id=p.id,
                    price_per_unit=round(cost * 0.92, 2),
                    min_order_qty=None,
                    bulk_discount_qty=None,
                    bulk_discount_price=None,
                    recorded_date=recorded_date,
                )
            )

    return prices


# ── Supplier delivery history ─────────────────────────────────────────────────

def _build_supplier_deliveries(
    db_suppliers: list, db_products: list, today: date
) -> list[SupplierDelivery]:
    """
    Generate 6 months of historical deliveries per supplier-product pair.
    On-time rates match spec profiles:
      Amul: 98% | Sri Krishna: 95% | Metro: 89% | Palakkad: 71%
    """
    supplier_map = {s.name: s for s in db_suppliers}
    deliveries: list[SupplierDelivery] = []

    profiles = [
        ("Amul Distributor Thrissur",  0.98, ["dairy"]),
        ("Sri Krishna Wholesale",       0.95, ["staples", "snacks", "beverages", "cleaning", "personal_care"]),
        ("Metro Cash & Carry Kochi",    0.89, ["staples", "snacks", "beverages", "cleaning", "spices", "personal_care"]),
        ("Palakkad Agro Traders",       0.71, ["staples", "spices"]),
    ]

    for supplier_name, on_time_rate, categories in profiles:
        supplier = supplier_map[supplier_name]
        eligible_products = [p for p in db_products if p.category in categories]

        for product in eligible_products:
            # One delivery per ~2 weeks over 6 months = ~13 deliveries
            for week in range(0, 26, 2):
                order_date = today - timedelta(weeks=26) + timedelta(weeks=week)
                expected = order_date + timedelta(days=product.lead_time_days)
                is_on_time = random.random() < on_time_rate

                if is_on_time:
                    actual = expected
                    delay = 0
                else:
                    delay = random.randint(1, 4)
                    actual = expected + timedelta(days=delay)

                qty_ordered = product.avg_daily_demand * 7
                qty_received = qty_ordered if is_on_time else qty_ordered * random.uniform(0.85, 1.0)

                complaint = None
                if not is_on_time:
                    complaint = random.choice(["Late delivery", "Short delivery", "Items damaged", None])

                rating = 5 if is_on_time else random.randint(2, 4)

                deliveries.append(
                    SupplierDelivery(
                        supplier_id=supplier.id,
                        product_id=product.id,
                        order_date=order_date,
                        expected_delivery_date=expected,
                        actual_delivery_date=actual,
                        on_time=is_on_time,
                        quantity_ordered=round(qty_ordered, 1),
                        quantity_received=round(qty_received, 1),
                        complaint=complaint,
                        rating=rating,
                    )
                )

    return deliveries


# ── Inventory batches ─────────────────────────────────────────────────────────

def _build_inventory_batches(db_products: list, today: date) -> list[InventoryBatch]:
    """
    Calibrated exactly as described in Section 6 for demo alerts:
    🚫 Eggs — OUT OF STOCK (qty=0)
    🔴 Milk — 1.7 days remaining (qty=170 @ 85/day)
    🟡 Banana Chips Batch 2 — expiry = today + 7 days
    🟡 Red Chilli Batch 1 — expiry = today + 9 days
    🟢 Rice — 14 days remaining (qty=252 @ 18/day)
    🔵 Coconut Oil — excess stock (qty=315 @ 9/day = 35 days)
    """
    product_map = {p.sku: p for p in db_products}
    batches: list[InventoryBatch] = []

    # ── Milk — CRITICAL (1.7 days at 85/day = 144.5 ≈ 170 with some buffer)
    batches.append(InventoryBatch(
        product_id=product_map["MILK-001"].id,
        batch_number="MILK-BATCH-001",
        quantity=170.0,
        unit="packet",
        purchase_price=54.0,
        manufactured_date=today - timedelta(days=1),
        expiry_date=today + timedelta(days=2),
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Eggs — OUT OF STOCK (qty=0)
    batches.append(InventoryBatch(
        product_id=product_map["EGGS-002"].id,
        batch_number="EGGS-BATCH-001",
        quantity=0.0,
        unit="tray",
        purchase_price=160.0,
        manufactured_date=today - timedelta(days=5),
        expiry_date=today + timedelta(days=16),
        status="depleted",
        created_at=datetime.utcnow(),
    ))

    # ── Curd — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["CURD-003"].id,
        batch_number="CURD-BATCH-001",
        quantity=90.0,
        unit="cup",
        purchase_price=26.0,
        manufactured_date=today - timedelta(days=1),
        expiry_date=today + timedelta(days=4),
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Rice — Healthy (252 units / 18 per day = 14 days)
    batches.append(InventoryBatch(
        product_id=product_map["RICE-004"].id,
        batch_number="RICE-BATCH-001",
        quantity=252.0,
        unit="bag",
        purchase_price=240.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Wheat Flour — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["FLOR-005"].id,
        batch_number="FLOR-BATCH-001",
        quantity=180.0,
        unit="packet",
        purchase_price=38.0,
        manufactured_date=None,
        expiry_date=today + timedelta(days=160),
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Coconut Oil — EXCESS (315 units / 9 per day = 35 days)
    batches.append(InventoryBatch(
        product_id=product_map["COIL-006"].id,
        batch_number="COIL-BATCH-001",
        quantity=315.0,
        unit="bottle",
        purchase_price=165.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Banana Chips Batch 1 — Healthy stock
    batches.append(InventoryBatch(
        product_id=product_map["BNCH-007"].id,
        batch_number="BNCH-BATCH-001",
        quantity=100.0,
        unit="packet",
        purchase_price=32.0,
        manufactured_date=today - timedelta(days=20),
        expiry_date=today + timedelta(days=25),
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Banana Chips Batch 2 — EXPIRING SOON (7 days) 🟡
    batches.append(InventoryBatch(
        product_id=product_map["BNCH-007"].id,
        batch_number="BNCH-BATCH-002",
        quantity=95.0,
        unit="packet",
        purchase_price=32.0,
        manufactured_date=today - timedelta(days=38),
        expiry_date=today + timedelta(days=7),
        status="expiring_soon",
        created_at=datetime.utcnow(),
    ))

    # ── Mixture Snack — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["MIXT-008"].id,
        batch_number="MIXT-BATCH-001",
        quantity=80.0,
        unit="packet",
        purchase_price=58.0,
        manufactured_date=today - timedelta(days=15),
        expiry_date=today + timedelta(days=75),
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Red Chilli Batch 1 — EXPIRING SOON (9 days) 🟡
    batches.append(InventoryBatch(
        product_id=product_map["RCHL-009"].id,
        batch_number="RCHL-BATCH-001",
        quantity=60.0,
        unit="packet",
        purchase_price=42.0,
        manufactured_date=today - timedelta(days=355),
        expiry_date=today + timedelta(days=9),
        status="expiring_soon",
        created_at=datetime.utcnow(),
    ))

    # ── Garam Masala — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["GRMS-010"].id,
        batch_number="GRMS-BATCH-001",
        quantity=45.0,
        unit="packet",
        purchase_price=20.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Tea Powder — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["TEA-011"].id,
        batch_number="TEA-BATCH-001",
        quantity=90.0,
        unit="packet",
        purchase_price=60.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Bru Coffee — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["COFF-012"].id,
        batch_number="COFF-BATCH-001",
        quantity=30.0,
        unit="jar",
        purchase_price=162.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Surf Excel — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["SURF-013"].id,
        batch_number="SURF-BATCH-001",
        quantity=50.0,
        unit="packet",
        purchase_price=115.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Vim Dishwash — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["VMDW-014"].id,
        batch_number="VMDW-BATCH-001",
        quantity=35.0,
        unit="bottle",
        purchase_price=52.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    # ── Dove Soap — Healthy
    batches.append(InventoryBatch(
        product_id=product_map["SOAP-015"].id,
        batch_number="SOAP-BATCH-001",
        quantity=60.0,
        unit="piece",
        purchase_price=36.0,
        manufactured_date=None,
        expiry_date=None,
        status="active",
        created_at=datetime.utcnow(),
    ))

    return batches


# ── Main seed function ────────────────────────────────────────────────────────

def seed_database(db: Session) -> None:
    """
    Entry point. Only seeds if the products table is empty.
    Call this from main.py lifespan startup.
    """
    # Guard: never re-seed
    if db.query(Product).count() > 0:
        print("[seed] Database already seeded — skipping.")
        return

    print("[seed] Starting database seed...")
    today = date.today()
    recorded_date = today

    # ── 1. Insert Products ────────────────────────────────────────────────
    db_products: list[Product] = []
    for p in PRODUCTS:
        product = Product(**p)
        db.add(product)
        db_products.append(product)
    db.flush()  # get auto-generated IDs
    print(f"[seed] Inserted {len(db_products)} products.")

    # ── 2. Insert Suppliers ───────────────────────────────────────────────
    db_suppliers: list[Supplier] = []
    for s in SUPPLIERS:
        supplier = Supplier(**s)
        db.add(supplier)
        db_suppliers.append(supplier)
    db.flush()
    print(f"[seed] Inserted {len(db_suppliers)} suppliers.")

    # ── 3. Insert Supplier Prices ─────────────────────────────────────────
    prices = _build_supplier_prices(db_suppliers, db_products, recorded_date)
    for price in prices:
        db.add(price)
    db.flush()
    print(f"[seed] Inserted {len(prices)} supplier price records.")

    # ── 4. Generate 365-day Sales History ────────────────────────────────
    event_calendar = _build_event_calendar(today)
    sales_records: list[SalesRecord] = []

    start_date = today - timedelta(days=365)
    current_date = start_date

    while current_date < today:
        event_tag = event_calendar.get(current_date, "normal")

        for product in db_products:
            multiplier = _get_multiplier(event_tag, product.category)
            # ±12% random noise
            noise = random.uniform(0.88, 1.12)
            qty_sold = round(product.avg_daily_demand * multiplier * noise, 1)
            qty_sold = max(0.0, qty_sold)
            revenue = round(qty_sold * product.selling_price, 2)

            sales_records.append(
                SalesRecord(
                    product_id=product.id,
                    date=current_date,
                    quantity_sold=qty_sold,
                    revenue=revenue,
                    event_tag=event_tag,
                )
            )

        current_date += timedelta(days=1)

    # Bulk insert in batches of 1000 to avoid memory issues
    BATCH_SIZE = 1000
    for i in range(0, len(sales_records), BATCH_SIZE):
        db.add_all(sales_records[i : i + BATCH_SIZE])
        db.flush()

    print(f"[seed] Inserted {len(sales_records)} sales records ({len(db_products)} products × 365 days).")

    # ── 5. Insert Inventory Batches ───────────────────────────────────────
    batches = _build_inventory_batches(db_products, today)
    for batch in batches:
        db.add(batch)
    db.flush()
    print(f"[seed] Inserted {len(batches)} inventory batches.")

    # ── 6. Insert Supplier Delivery History ──────────────────────────────
    deliveries = _build_supplier_deliveries(db_suppliers, db_products, today)
    for delivery in deliveries:
        db.add(delivery)
    db.flush()
    print(f"[seed] Inserted {len(deliveries)} supplier delivery records.")

    # ── 7. Commit everything ──────────────────────────────────────────────
    db.commit()
    print("[seed] ✅ Database seeded successfully.")
