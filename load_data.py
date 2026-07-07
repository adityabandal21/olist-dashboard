import pandas as pd
import sqlite3
import os

DB_PATH = "data/olist.db"

def load_database():
    if os.path.exists(DB_PATH):
        return sqlite3.connect(DB_PATH)

    print("Building SQLite database from CSVs...")
    conn = sqlite3.connect(DB_PATH)

    tables = {
        "orders": "data/olist_orders_dataset.csv",
        "customers": "data/olist_customers_dataset.csv",
        "order_items": "data/olist_order_items_dataset.csv",
        "order_payments": "data/olist_order_payments_dataset.csv",
        "order_reviews": "data/olist_order_reviews_dataset.csv",
        "products": "data/olist_products_dataset.csv",
        "sellers": "data/olist_sellers_dataset.csv",
        "category_translation": "data/product_category_name_translation.csv",
        "geolocation": "data/olist_geolocation_dataset.csv"
    }

    for table_name, path in tables.items():
        df = pd.read_csv(path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  Loaded {table_name}: {len(df):,} rows")

    print("Database ready!")
    return conn

def query(sql):
    conn = sqlite3.connect(DB_PATH)
    return pd.read_sql_query(sql, conn)
