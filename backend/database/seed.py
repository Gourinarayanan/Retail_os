"""
RetailWise AI — Database Seeder (Expanded 50-Product Edition)
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

random.seed(42)

PRODUCTS = [
    # ── DAIRY (daily order) ────────────────────────────────────────────────
    {
        "name": "Milk 1L Packet", "sku": "MILK-001", "category": "dairy", "brand": "Milma",
        "unit": "packet", "unit_size": 1.0, "selling_price": 62, "cost_price": 54,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 2, "min_threshold": 50, "demand_events": "hartal_pre,onam,christmas,rainy_day",
        "avg_daily_demand": 85,
    },
    {
        "name": "Eggs Tray (30)", "sku": "EGGS-002", "category": "dairy", "brand": None,
        "unit": "tray", "unit_size": 30.0, "selling_price": 185, "cost_price": 160,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 21, "min_threshold": 8, "demand_events": "hartal_pre,christmas,easter",
        "avg_daily_demand": 12,
    },
    {
        "name": "Curd 500ml", "sku": "CURD-003", "category": "dairy", "brand": "Milma",
        "unit": "cup", "unit_size": 0.5, "selling_price": 32, "cost_price": 26,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 5, "min_threshold": 20, "demand_events": "onam,summer",
        "avg_daily_demand": 30,
    },
    {
        "name": "Butter 100g", "sku": "BTR-001", "category": "dairy", "brand": "Amul",
        "unit": "piece", "unit_size": 0.1, "selling_price": 60, "cost_price": 50,
        "order_cycle": "weekly", "order_day": "Monday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 90, "min_threshold": 10, "demand_events": "christmas,onam",
        "avg_daily_demand": 8,
    },
    {
        "name": "Paneer 200g", "sku": "PNR-001", "category": "dairy", "brand": "Amul",
        "unit": "packet", "unit_size": 0.2, "selling_price": 95, "cost_price": 80,
        "order_cycle": "weekly", "order_day": "Tuesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 30, "min_threshold": 5, "demand_events": "weekend",
        "avg_daily_demand": 6,
    },
    {
        "name": "Cheese Slices 100g", "sku": "CHS-001", "category": "dairy", "brand": "Amul",
        "unit": "packet", "unit_size": 0.1, "selling_price": 85, "cost_price": 70,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 5, "demand_events": "weekend",
        "avg_daily_demand": 5,
    },

    # ── PRODUCE (daily order) ──────────────────────────────────────────────
    {
        "name": "Onion 1kg", "sku": "ONN-001", "category": "produce", "brand": None,
        "unit": "kg", "unit_size": 1.0, "selling_price": 45, "cost_price": 32,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 3.0, "lead_time_days": 1,
        "shelf_life_days": 14, "min_threshold": 20, "demand_events": "hartal_pre,eid,ramadan",
        "avg_daily_demand": 40,
    },
    {
        "name": "Tomato 1kg", "sku": "TOM-001", "category": "produce", "brand": None,
        "unit": "kg", "unit_size": 1.0, "selling_price": 35, "cost_price": 25,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 5, "min_threshold": 15, "demand_events": "hartal_pre",
        "avg_daily_demand": 35,
    },
    {
        "name": "Potato 1kg", "sku": "POT-001", "category": "produce", "brand": None,
        "unit": "kg", "unit_size": 1.0, "selling_price": 40, "cost_price": 28,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 3.0, "lead_time_days": 1,
        "shelf_life_days": 20, "min_threshold": 20, "demand_events": "hartal_pre,eid",
        "avg_daily_demand": 30,
    },
    {
        "name": "Nendran Banana 1kg", "sku": "BAN-001", "category": "produce", "brand": None,
        "unit": "kg", "unit_size": 1.0, "selling_price": 65, "cost_price": 50,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 4, "min_threshold": 10, "demand_events": "onam,vishu",
        "avg_daily_demand": 25,
    },
    {
        "name": "Coconut (Piece)", "sku": "COC-001", "category": "produce", "brand": None,
        "unit": "piece", "unit_size": 1.0, "selling_price": 30, "cost_price": 20,
        "order_cycle": "weekly", "order_day": "Thursday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 10, "min_threshold": 20, "demand_events": "onam,vishu,eid",
        "avg_daily_demand": 45,
    },
    {
        "name": "Green Chilli 250g", "sku": "GCH-001", "category": "produce", "brand": None,
        "unit": "packet", "unit_size": 0.25, "selling_price": 20, "cost_price": 12,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 5, "min_threshold": 5, "demand_events": "",
        "avg_daily_demand": 15,
    },
    {
        "name": "Ginger 250g", "sku": "GIN-001", "category": "produce", "brand": None,
        "unit": "packet", "unit_size": 0.25, "selling_price": 40, "cost_price": 28,
        "order_cycle": "weekly", "order_day": "Tuesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 14, "min_threshold": 5, "demand_events": "ramadan,eid",
        "avg_daily_demand": 10,
    },
    {
        "name": "Garlic 250g", "sku": "GAR-001", "category": "produce", "brand": None,
        "unit": "packet", "unit_size": 0.25, "selling_price": 50, "cost_price": 35,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 30, "min_threshold": 5, "demand_events": "ramadan,eid",
        "avg_daily_demand": 12,
    },
    {
        "name": "Carrot 1kg", "sku": "CAR-001", "category": "produce", "brand": None,
        "unit": "kg", "unit_size": 1.0, "selling_price": 60, "cost_price": 45,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 7, "min_threshold": 10, "demand_events": "weekend",
        "avg_daily_demand": 18,
    },
    {
        "name": "Cabbage 1kg", "sku": "CAB-001", "category": "produce", "brand": None,
        "unit": "kg", "unit_size": 1.0, "selling_price": 30, "cost_price": 20,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 7, "min_threshold": 8, "demand_events": "",
        "avg_daily_demand": 12,
    },

    # ── MEAT (daily order) ─────────────────────────────────────────────────
    {
        "name": "Frozen Chicken 1kg", "sku": "CHK-001", "category": "meat", "brand": "Suguna",
        "unit": "packet", "unit_size": 1.0, "selling_price": 180, "cost_price": 140,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 60, "min_threshold": 15, "demand_events": "weekend,eid,christmas",
        "avg_daily_demand": 22,
    },
    {
        "name": "Frozen Beef 500g", "sku": "BEEF-001", "category": "meat", "brand": "Local Meat",
        "unit": "packet", "unit_size": 0.5, "selling_price": 190, "cost_price": 150,
        "order_cycle": "daily", "order_day": None, "reorder_point_days": 2.0, "lead_time_days": 1,
        "shelf_life_days": 60, "min_threshold": 10, "demand_events": "weekend,eid,christmas",
        "avg_daily_demand": 15,
    },
    {
        "name": "Chicken Sausages 250g", "sku": "SAU-001", "category": "meat", "brand": "Sumeru",
        "unit": "packet", "unit_size": 0.25, "selling_price": 120, "cost_price": 95,
        "order_cycle": "weekly", "order_day": "Friday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 90, "min_threshold": 5, "demand_events": "weekend",
        "avg_daily_demand": 8,
    },

    # ── STAPLES ────────────────────────────────────────────────────────────
    {
        "name": "Ponni Rice 5kg", "sku": "RICE-004", "category": "staples", "brand": None,
        "unit": "bag", "unit_size": 5.0, "selling_price": 280, "cost_price": 240,
        "order_cycle": "weekly", "order_day": "Monday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 9999, "min_threshold": 30, "demand_events": "hartal_pre,onam,vishu,eid,ramadan",
        "avg_daily_demand": 18,
    },
    {
        "name": "Wheat Flour 1kg", "sku": "FLOR-005", "category": "staples", "brand": "Aashirvaad",
        "unit": "packet", "unit_size": 1.0, "selling_price": 48, "cost_price": 38,
        "order_cycle": "weekly", "order_day": "Monday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 40, "demand_events": "hartal_pre,ramadan,christmas",
        "avg_daily_demand": 22,
    },
    {
        "name": "Coconut Oil 1L", "sku": "COIL-006", "category": "staples", "brand": "KPL Shudhi",
        "unit": "bottle", "unit_size": 1.0, "selling_price": 195, "cost_price": 165,
        "order_cycle": "weekly", "order_day": "Monday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 9999, "min_threshold": 15, "demand_events": "hartal_pre,onam,vishu",
        "avg_daily_demand": 9,
    },
    {
        "name": "Toor Dal 1kg", "sku": "DAL-001", "category": "staples", "brand": "Tata Sampann",
        "unit": "packet", "unit_size": 1.0, "selling_price": 160, "cost_price": 130,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 15, "demand_events": "hartal_pre,ramadan",
        "avg_daily_demand": 12,
    },
    {
        "name": "Moong Dal 1kg", "sku": "DAL-002", "category": "staples", "brand": "Tata Sampann",
        "unit": "packet", "unit_size": 1.0, "selling_price": 140, "cost_price": 115,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 10, "demand_events": "hartal_pre,onam",
        "avg_daily_demand": 10,
    },
    {
        "name": "Sugar 1kg", "sku": "SUG-001", "category": "staples", "brand": "Madhur",
        "unit": "packet", "unit_size": 1.0, "selling_price": 45, "cost_price": 38,
        "order_cycle": "weekly", "order_day": "Thursday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 9999, "min_threshold": 20, "demand_events": "hartal_pre,onam,eid,christmas",
        "avg_daily_demand": 25,
    },
    {
        "name": "Salt 1kg", "sku": "SLT-001", "category": "staples", "brand": "Tata Salt",
        "unit": "packet", "unit_size": 1.0, "selling_price": 25, "cost_price": 18,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 30, "demand_events": "hartal_pre",
        "avg_daily_demand": 15,
    },
    {
        "name": "Sunflower Oil 1L", "sku": "OIL-002", "category": "staples", "brand": "Sunpure",
        "unit": "bottle", "unit_size": 1.0, "selling_price": 145, "cost_price": 125,
        "order_cycle": "weekly", "order_day": "Monday", "reorder_point_days": 7.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 15, "demand_events": "hartal_pre,eid,ramadan",
        "avg_daily_demand": 14,
    },

    # ── SPICES ─────────────────────────────────────────────────────────────
    {
        "name": "Red Chilli Powder 200g", "sku": "RCHL-009", "category": "spices", "brand": "Eastern",
        "unit": "packet", "unit_size": 0.2, "selling_price": 55, "cost_price": 42,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 20, "demand_events": "ramadan,eid,onam",
        "avg_daily_demand": 14,
    },
    {
        "name": "Garam Masala 50g", "sku": "GRMS-010", "category": "spices", "brand": "Eastern",
        "unit": "packet", "unit_size": 0.05, "selling_price": 28, "cost_price": 20,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 12, "demand_events": "ramadan,eid,christmas",
        "avg_daily_demand": 8,
    },
    {
        "name": "Turmeric Powder 100g", "sku": "TUR-001", "category": "spices", "brand": "Eastern",
        "unit": "packet", "unit_size": 0.1, "selling_price": 30, "cost_price": 22,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 15, "demand_events": "onam",
        "avg_daily_demand": 10,
    },
    {
        "name": "Coriander Powder 200g", "sku": "COR-001", "category": "spices", "brand": "Eastern",
        "unit": "packet", "unit_size": 0.2, "selling_price": 45, "cost_price": 32,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 15, "demand_events": "ramadan,eid",
        "avg_daily_demand": 12,
    },
    {
        "name": "Black Pepper 50g", "sku": "PEP-001", "category": "spices", "brand": "Eastern",
        "unit": "packet", "unit_size": 0.05, "selling_price": 60, "cost_price": 45,
        "order_cycle": "weekly", "order_day": "Wednesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 10, "demand_events": "christmas",
        "avg_daily_demand": 6,
    },
    {
        "name": "Mustard Seeds 100g", "sku": "MUS-001", "category": "spices", "brand": "Local",
        "unit": "packet", "unit_size": 0.1, "selling_price": 25, "cost_price": 16,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 10, "demand_events": "onam,vishu",
        "avg_daily_demand": 5,
    },

    # ── SNACKS & BEVERAGES ─────────────────────────────────────────────────
    {
        "name": "Banana Chips 200g", "sku": "BNCH-007", "category": "snacks", "brand": "Local",
        "unit": "packet", "unit_size": 0.2, "selling_price": 45, "cost_price": 32,
        "order_cycle": "weekly", "order_day": "Thursday", "reorder_point_days": 5.0, "lead_time_days": 1,
        "shelf_life_days": 45, "min_threshold": 50, "demand_events": "hartal_pre,onam,vishu,rainy_day",
        "avg_daily_demand": 42,
    },
    {
        "name": "Mixture Snack 500g", "sku": "MIXT-008", "category": "snacks", "brand": "Local",
        "unit": "packet", "unit_size": 0.5, "selling_price": 80, "cost_price": 58,
        "order_cycle": "weekly", "order_day": "Thursday", "reorder_point_days": 5.0, "lead_time_days": 1,
        "shelf_life_days": 90, "min_threshold": 25, "demand_events": "onam,christmas,eid,rainy_day",
        "avg_daily_demand": 18,
    },
    {
        "name": "Tea Powder 250g", "sku": "TEA-011", "category": "beverages", "brand": "Kannan Devan",
        "unit": "packet", "unit_size": 0.25, "selling_price": 75, "cost_price": 60,
        "order_cycle": "weekly", "order_day": "Tuesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 25, "demand_events": "hartal_pre,rainy_day,onam",
        "avg_daily_demand": 16,
    },
    {
        "name": "Bru Coffee 200g", "sku": "COFF-012", "category": "beverages", "brand": "Bru",
        "unit": "jar", "unit_size": 0.2, "selling_price": 195, "cost_price": 162,
        "order_cycle": "weekly", "order_day": "Tuesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 365, "min_threshold": 8, "demand_events": "christmas,vishu",
        "avg_daily_demand": 5,
    },
    {
        "name": "Parle-G 100g", "sku": "PAR-001", "category": "snacks", "brand": "Parle",
        "unit": "packet", "unit_size": 0.1, "selling_price": 10, "cost_price": 8,
        "order_cycle": "weekly", "order_day": "Thursday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 30, "demand_events": "rainy_day",
        "avg_daily_demand": 20,
    },
    {
        "name": "Good Day 100g", "sku": "GD-001", "category": "snacks", "brand": "Britannia",
        "unit": "packet", "unit_size": 0.1, "selling_price": 20, "cost_price": 15,
        "order_cycle": "weekly", "order_day": "Thursday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 20, "demand_events": "weekend",
        "avg_daily_demand": 15,
    },
    {
        "name": "Lays Classic 50g", "sku": "LAY-001", "category": "snacks", "brand": "Lays",
        "unit": "packet", "unit_size": 0.05, "selling_price": 20, "cost_price": 16,
        "order_cycle": "weekly", "order_day": "Friday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 25, "demand_events": "weekend,rainy_day",
        "avg_daily_demand": 25,
    },
    {
        "name": "Coca-Cola 1.5L", "sku": "COK-001", "category": "beverages", "brand": "Coca-Cola",
        "unit": "bottle", "unit_size": 1.5, "selling_price": 95, "cost_price": 80,
        "order_cycle": "weekly", "order_day": "Tuesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 15, "demand_events": "weekend,summer,eid",
        "avg_daily_demand": 10,
    },
    {
        "name": "Mango Juice 1L", "sku": "MNG-001", "category": "beverages", "brand": "Tropicana",
        "unit": "carton", "unit_size": 1.0, "selling_price": 110, "cost_price": 90,
        "order_cycle": "weekly", "order_day": "Tuesday", "reorder_point_days": 5.0, "lead_time_days": 2,
        "shelf_life_days": 180, "min_threshold": 10, "demand_events": "summer,ramadan",
        "avg_daily_demand": 8,
    },

    # ── CLEANING, PERSONAL CARE, BABY CARE ────────────────────────────────
    {
        "name": "Surf Excel 1kg", "sku": "SURF-013", "category": "cleaning", "brand": "Surf Excel",
        "unit": "packet", "unit_size": 1.0, "selling_price": 138, "cost_price": 115,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 10, "demand_events": "onam,vishu",
        "avg_daily_demand": 6,
    },
    {
        "name": "Vim Dishwash 500ml", "sku": "VMDW-014", "category": "cleaning", "brand": "Vim",
        "unit": "bottle", "unit_size": 0.5, "selling_price": 65, "cost_price": 52,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 8, "demand_events": "onam",
        "avg_daily_demand": 4,
    },
    {
        "name": "Harpic Toilet Cleaner 500ml", "sku": "HAR-001", "category": "cleaning", "brand": "Harpic",
        "unit": "bottle", "unit_size": 0.5, "selling_price": 95, "cost_price": 75,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 8, "demand_events": "onam,vishu",
        "avg_daily_demand": 3,
    },
    {
        "name": "Dove Soap 100g", "sku": "SOAP-015", "category": "personal_care", "brand": "Dove",
        "unit": "piece", "unit_size": 0.1, "selling_price": 45, "cost_price": 36,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 12, "demand_events": "onam,vishu,christmas",
        "avg_daily_demand": 8,
    },
    {
        "name": "Colgate Toothpaste 100g", "sku": "COL-001", "category": "personal_care", "brand": "Colgate",
        "unit": "piece", "unit_size": 0.1, "selling_price": 60, "cost_price": 48,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 10, "demand_events": "onam,vishu",
        "avg_daily_demand": 6,
    },
    {
        "name": "Pampers Diapers (M)", "sku": "PAM-001", "category": "baby_care", "brand": "Pampers",
        "unit": "packet", "unit_size": 1.0, "selling_price": 450, "cost_price": 380,
        "order_cycle": "weekly", "order_day": "Friday", "reorder_point_days": 7.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 5, "demand_events": "hartal_pre",
        "avg_daily_demand": 3,
    },
    {
        "name": "Johnson's Baby Soap 100g", "sku": "JBS-001", "category": "baby_care", "brand": "Johnsons",
        "unit": "piece", "unit_size": 0.1, "selling_price": 65, "cost_price": 52,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 9999, "min_threshold": 6, "demand_events": "",
        "avg_daily_demand": 2,
    },
    {
        "name": "Baby Wipes (80s)", "sku": "WIP-001", "category": "baby_care", "brand": "Himalaya",
        "unit": "packet", "unit_size": 1.0, "selling_price": 120, "cost_price": 95,
        "order_cycle": "monthly", "order_day": "1", "reorder_point_days": 10.0, "lead_time_days": 3,
        "shelf_life_days": 720, "min_threshold": 5, "demand_events": "hartal_pre",
        "avg_daily_demand": 2,
    },
]

SUPPLIERS = [
    {
        "name": "Sri Krishna Wholesale", "contact_name": "Krishna Nair", "whatsapp_number": "+919876543210", "email": "srikrishna.wholesale@gmail.com", "region": "Thrissur",
        "supply_categories": "staples,snacks,beverages,cleaning,personal_care,baby_care", "notes": "Highly trusted local supplier. Price +3% vs market avg. 95% on-time reliability.", "is_active": True,
    },
    {
        "name": "Palakkad Agro Traders", "contact_name": "Suresh Kumar", "whatsapp_number": "+919865432100", "email": "palakkad.agro@gmail.com", "region": "Palakkad",
        "supply_categories": "staples,spices", "notes": "Cheapest prices (-8% vs market avg) but 71% reliability. Frequently late. Rain risk.", "is_active": True,
    },
    {
        "name": "Amul Distributor Thrissur", "contact_name": "Anoop Varma", "whatsapp_number": "+919854321000", "email": "amul.thrissur@amuldairy.com", "region": "Thrissur",
        "supply_categories": "dairy", "notes": "Fixed MRP-based pricing. 98% on-time. Only dairy supplier in network.", "is_active": True,
    },
    {
        "name": "Metro Cash & Carry Kochi", "contact_name": "Priya Menon", "whatsapp_number": "+919843210000", "email": "priya.menon@metro.in", "region": "Kochi",
        "supply_categories": "staples,snacks,beverages,cleaning,spices,personal_care,baby_care", "notes": "Good for weekly bulk orders. -5% vs market avg. 89% reliability.", "is_active": True,
    },
    {
        "name": "Thrissur Fresh Produce", "contact_name": "Raju Chettan", "whatsapp_number": "+919832100000", "email": "raju.produce@gmail.com", "region": "Thrissur",
        "supply_categories": "produce", "notes": "Daily fresh veggies. Prices fluctuate daily. 92% reliability.", "is_active": True,
    },
    {
        "name": "Suguna Meats Distributor", "contact_name": "Mohammed Ali", "whatsapp_number": "+919821000000", "email": "ali.meats@suguna.com", "region": "Thrissur",
        "supply_categories": "meat", "notes": "Frozen meats. 97% reliability.", "is_active": True,
    },
]

EVENT_MULTIPLIERS: dict[str, dict] = {
    "hartal_pre": {"dairy": 1.80, "staples": 1.60, "snacks": 1.65, "beverages": 1.45, "spices": 1.30, "cleaning": 1.10, "personal_care": 1.05, "produce": 1.50, "meat": 1.70, "baby_care": 1.30},
    "hartal_day": {"_all": 0.08},
    "hartal_post": {"_all": 1.15},
    "onam": {"snacks": 1.45, "staples": 1.35, "dairy": 1.25, "beverages": 1.20, "cleaning": 1.20, "personal_care": 1.15, "produce": 1.40, "meat": 1.50},
    "vishu": {"staples": 1.30, "snacks": 1.25, "cleaning": 1.15, "personal_care": 1.20, "produce": 1.30, "meat": 1.40},
    "ramadan": {"spices": 1.55, "staples": 1.30, "dairy": 1.20, "beverages": 1.10, "meat": 1.60, "produce": 1.30},
    "eid": {"spices": 1.85, "staples": 1.50, "snacks": 1.55, "dairy": 1.40, "meat": 2.00},
    "christmas": {"beverages": 1.50, "snacks": 1.45, "dairy": 1.35, "staples": 1.30, "personal_care": 1.25, "meat": 1.60},
    "rainy_day": {"beverages": 1.30, "snacks": 1.25, "dairy": 1.10, "_all": 0.92},
    "weekend": {"_all": 1.10, "produce": 1.20, "meat": 1.30},
    "normal": {"_all": 1.00},
}

ALL_CATEGORIES = ("dairy", "staples", "snacks", "spices", "beverages", "cleaning", "personal_care", "produce", "meat", "baby_care")

def _build_event_calendar(today: date) -> dict[date, str]:
    start = today - timedelta(days=365)
    calendar: dict[date, str] = {}
    hartal_days: set[date] = set()
    for offset_days in [30, 95, 180, 255, 330]: hartal_days.add(start + timedelta(days=offset_days))
    onam_days: set[date] = set()
    for year in {start.year, today.year}:
        for i in range(10):
            d = date(year, 9, 10) + timedelta(days=i)
            if start <= d <= today: onam_days.add(d)
    vishu_days: set[date] = set()
    for year in {start.year, today.year}:
        vd = date(year, 4, 14)
        if start <= vd <= today:
            for i in range(3):
                d = vd + timedelta(days=i)
                if start <= d <= today: vishu_days.add(d)
    ramadan_days: set[date] = set()
    for year in {start.year, today.year}:
        ram_start = date(year, 3, 1)
        for i in range(30):
            d = ram_start + timedelta(days=i)
            if start <= d <= today: ramadan_days.add(d)
    eid_days: set[date] = set()
    for year in {start.year, today.year}:
        eid_start = date(year, 3, 28)
        for i in range(3):
            d = eid_start + timedelta(days=i)
            if start <= d <= today: eid_days.add(d)
    christmas_days: set[date] = set()
    for year in {start.year, today.year}:
        for day in range(20, 28):
            d = date(year, 12, day)
            if start <= d <= today: christmas_days.add(d)
    rainy_days: set[date] = set()
    current = start
    while current <= today:
        if current.month in (6, 7, 8) and current.day % 3 == 0: rainy_days.add(current)
        current += timedelta(days=1)
    current = start
    while current <= today:
        if current in hartal_days: tag = "hartal_day"
        elif (current - timedelta(days=1)) in hartal_days: tag = "hartal_pre"
        elif (current + timedelta(days=1)) in hartal_days: tag = "hartal_post"
        elif current in eid_days: tag = "eid"
        elif current in onam_days: tag = "onam"
        elif current in vishu_days: tag = "vishu"
        elif current in ramadan_days: tag = "ramadan"
        elif current in christmas_days: tag = "christmas"
        elif current in rainy_days: tag = "rainy_day"
        elif current.weekday() in (5, 6): tag = "weekend"
        else: tag = "normal"
        calendar[current] = tag
        current += timedelta(days=1)
    return calendar

def _get_multiplier(event_tag: str, category: str) -> float:
    impacts = EVENT_MULTIPLIERS.get(event_tag, {"_all": 1.0})
    mult = impacts.get(category, impacts.get("_all", 1.0))
    if event_tag == "rainy_day" and category in impacts and "_all" in impacts:
        mult = impacts[category] * impacts["_all"]
    return float(mult)

def _build_supplier_prices(db_suppliers: list, db_products: list, recorded_date: date) -> list[SupplierPrice]:
    supplier_map = {s.name: s for s in db_suppliers}
    prices: list[SupplierPrice] = []
    for p in db_products:
        cost = p.cost_price
        if p.category == "dairy":
            prices.append(SupplierPrice(supplier_id=supplier_map["Amul Distributor Thrissur"].id, product_id=p.id, price_per_unit=round(cost, 2), recorded_date=recorded_date))
        if p.category in ("staples", "snacks", "beverages", "cleaning", "personal_care", "baby_care"):
            prices.append(SupplierPrice(supplier_id=supplier_map["Sri Krishna Wholesale"].id, product_id=p.id, price_per_unit=round(cost * 1.03, 2), recorded_date=recorded_date))
        if p.category in ("staples", "snacks", "beverages", "cleaning", "spices", "personal_care", "baby_care"):
            prices.append(SupplierPrice(supplier_id=supplier_map["Metro Cash & Carry Kochi"].id, product_id=p.id, price_per_unit=round(cost * 0.95, 2), min_order_qty=10, bulk_discount_qty=50, bulk_discount_price=round(cost * 0.92, 2), recorded_date=recorded_date))
        if p.category in ("staples", "spices"):
            prices.append(SupplierPrice(supplier_id=supplier_map["Palakkad Agro Traders"].id, product_id=p.id, price_per_unit=round(cost * 0.92, 2), recorded_date=recorded_date))
        if p.category == "produce":
            prices.append(SupplierPrice(supplier_id=supplier_map["Thrissur Fresh Produce"].id, product_id=p.id, price_per_unit=round(cost, 2), recorded_date=recorded_date))
        if p.category == "meat":
            prices.append(SupplierPrice(supplier_id=supplier_map["Suguna Meats Distributor"].id, product_id=p.id, price_per_unit=round(cost, 2), recorded_date=recorded_date))
    return prices

def _build_supplier_deliveries(db_suppliers: list, db_products: list, today: date) -> list[SupplierDelivery]:
    supplier_map = {s.name: s for s in db_suppliers}
    deliveries: list[SupplierDelivery] = []
    profiles = [
        ("Amul Distributor Thrissur",  0.98, ["dairy"]),
        ("Sri Krishna Wholesale",       0.95, ["staples", "snacks", "beverages", "cleaning", "personal_care", "baby_care"]),
        ("Metro Cash & Carry Kochi",    0.89, ["staples", "snacks", "beverages", "cleaning", "spices", "personal_care", "baby_care"]),
        ("Palakkad Agro Traders",       0.71, ["staples", "spices"]),
        ("Thrissur Fresh Produce",      0.92, ["produce"]),
        ("Suguna Meats Distributor",    0.97, ["meat"]),
    ]
    for supplier_name, on_time_rate, categories in profiles:
        supplier = supplier_map[supplier_name]
        eligible_products = [p for p in db_products if p.category in categories]
        for product in eligible_products:
            for week in range(0, 26, 2):
                order_date = today - timedelta(weeks=26) + timedelta(weeks=week)
                expected = order_date + timedelta(days=product.lead_time_days)
                is_on_time = random.random() < on_time_rate
                delay = 0 if is_on_time else random.randint(1, 4)
                actual = expected + timedelta(days=delay)
                qty_ordered = product.avg_daily_demand * 7
                qty_received = qty_ordered if is_on_time else qty_ordered * random.uniform(0.85, 1.0)
                complaint = None if is_on_time else random.choice(["Late delivery", "Short delivery", "Items damaged", None])
                rating = 5 if is_on_time else random.randint(2, 4)
                deliveries.append(SupplierDelivery(supplier_id=supplier.id, product_id=product.id, order_date=order_date, expected_delivery_date=expected, actual_delivery_date=actual, on_time=is_on_time, quantity_ordered=round(qty_ordered, 1), quantity_received=round(qty_received, 1), complaint=complaint, rating=rating))
    return deliveries

def _build_inventory_batches(db_products: list, today: date) -> list[InventoryBatch]:
    product_map = {p.sku: p for p in db_products}
    batches: list[InventoryBatch] = []

    # Hardcoded demo alerts
    # MILK: Critical
    if "MILK-001" in product_map:
        batches.append(InventoryBatch(product_id=product_map["MILK-001"].id, batch_number="MILK-BATCH-001", quantity=170.0, unit="packet", purchase_price=54.0, manufactured_date=today - timedelta(days=1), expiry_date=today + timedelta(days=2), status="active", created_at=datetime.utcnow()))
    # EGGS: Depleted
    if "EGGS-002" in product_map:
        batches.append(InventoryBatch(product_id=product_map["EGGS-002"].id, batch_number="EGGS-BATCH-001", quantity=0.0, unit="tray", purchase_price=160.0, manufactured_date=today - timedelta(days=5), expiry_date=today + timedelta(days=16), status="depleted", created_at=datetime.utcnow()))
    # BANANA CHIPS: Expiring soon
    if "BNCH-007" in product_map:
        batches.append(InventoryBatch(product_id=product_map["BNCH-007"].id, batch_number="BNCH-BATCH-002", quantity=95.0, unit="packet", purchase_price=32.0, manufactured_date=today - timedelta(days=38), expiry_date=today + timedelta(days=7), status="expiring_soon", created_at=datetime.utcnow()))
    
    # Dynamic generation for the rest
    for p in db_products:
        if p.sku in ["MILK-001", "EGGS-002", "BNCH-007"]: continue
        
        # Give everyone 14 days of healthy stock
        qty = p.avg_daily_demand * 14.0
        exp = today + timedelta(days=p.shelf_life_days) if p.shelf_life_days < 9999 else None
        batches.append(InventoryBatch(
            product_id=p.id,
            batch_number=f"{p.sku}-BATCH-001",
            quantity=qty,
            unit=p.unit,
            purchase_price=p.cost_price,
            manufactured_date=today - timedelta(days=2),
            expiry_date=exp,
            status="active",
            created_at=datetime.utcnow(),
        ))
    return batches

def _generate_sales_records(db_products: list, calendar: dict[date, str]) -> list[SalesRecord]:
    records: list[SalesRecord] = []
    for p in db_products:
        for d, tag in calendar.items():
            mult = _get_multiplier(tag, p.category)
            # Add ±15% noise
            noise = random.uniform(0.85, 1.15)
            qty = p.avg_daily_demand * mult * noise
            # Force 0 on hartal day unless noise allows a tiny bit
            if tag == "hartal_day": qty = p.avg_daily_demand * 0.08 * noise
            # Round to sensible units
            if p.unit in ("packet", "piece", "bottle", "tray", "jar", "cup"):
                qty = round(qty)
            else:
                qty = round(qty, 1)
            # Don't let it go below 0
            qty = max(0.0, qty)
            rev = round(qty * p.selling_price, 2)
            records.append(SalesRecord(product_id=p.id, date=d, quantity_sold=qty, revenue=rev, event_tag=tag))
    return records

def seed_database(db: Session) -> None:
    if db.query(Product).count() > 0:
        return
    today = date.today()
    # 1. Products
    db_products = []
    for p_data in PRODUCTS:
        p = Product(**p_data)
        db_products.append(p)
        db.add(p)
    db.commit()
    for p in db_products: db.refresh(p)
    # 2. Suppliers
    db_suppliers = []
    for s_data in SUPPLIERS:
        s = Supplier(**s_data)
        db_suppliers.append(s)
        db.add(s)
    db.commit()
    for s in db_suppliers: db.refresh(s)
    # 3. Calendar & Prices
    calendar = _build_event_calendar(today)
    prices = _build_supplier_prices(db_suppliers, db_products, today)
    db.add_all(prices)
    db.commit()
    # 4. Deliveries
    deliveries = _build_supplier_deliveries(db_suppliers, db_products, today)
    db.add_all(deliveries)
    db.commit()
    # 5. Batches
    batches = _build_inventory_batches(db_products, today)
    db.add_all(batches)
    db.commit()
    # 6. Sales
    sales = _generate_sales_records(db_products, calendar)
    # Batch insert sales
    batch_size = 5000
    for i in range(0, len(sales), batch_size):
        db.add_all(sales[i:i+batch_size])
        db.commit()
