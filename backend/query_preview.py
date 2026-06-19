import sqlite3
import pandas as pd

conn = sqlite3.connect('database/retailwise.db')

print('\n--- PRODUCTS TABLE (First 5 Items) ---')
print(pd.read_sql('SELECT id, sku, name, category, avg_daily_demand FROM products LIMIT 5', conn))

print('\n--- RECENT SALES DATA (Past 5 days for MILK-001) ---')
print(pd.read_sql('SELECT s.date, p.sku, s.quantity_sold, s.event_tag FROM sales_records s JOIN products p ON s.product_id = p.id WHERE p.sku="MILK-001" ORDER BY s.date DESC LIMIT 5', conn))

conn.close()
