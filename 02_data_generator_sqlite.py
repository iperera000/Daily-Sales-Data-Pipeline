#!/usr/bin/env python3
"""
02_data_generator.py (SQLite Version)
Generates sample sales data and inserts it into the raw_sales table.
Can be run manually or called by the scheduler.
"""

import sqlite3
from datetime import datetime
import random
import string
import config_sqlite as config

class SalesDataGenerator:
    """Generate realistic sales data."""

    PRODUCTS = [
        ("Laptop", "Electronics", 899.99),
        ("Mouse", "Electronics", 25.50),
        ("Keyboard", "Electronics", 75.00),
        ("Monitor", "Electronics", 299.99),
        ("Headphones", "Electronics", 149.99),
        ("T-Shirt", "Clothing", 19.99),
        ("Jeans", "Clothing", 49.99),
        ("Shoes", "Clothing", 79.99),
        ("Jacket", "Clothing", 89.99),
        ("Hat", "Clothing", 24.99),
        ("Coffee Maker", "Home", 89.99),
        ("Blender", "Home", 59.99),
        ("Microwave", "Home", 199.99),
        ("Toaster", "Home", 39.99),
        ("Vacuum", "Home", 299.99),
    ]

    REGIONS = ["North", "South", "East", "West", "Central"]
    CATEGORIES = list(set([p[1] for p in PRODUCTS]))

    @staticmethod
    def generate_transaction_id():
        """Generate unique transaction ID."""
        return "TXN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    @staticmethod
    def generate_customer_id():
        """Generate customer ID."""
        return "CUST-" + str(random.randint(10000, 99999))

    @classmethod
    def generate_sales_records(cls, count=100):
        """Generate sample sales records."""
        records = []
        base_date = datetime.now().date()

        for _ in range(count):
            # Random product
            product_name, category, unit_price = random.choice(cls.PRODUCTS)

            # Random variations in price (discount/premium)
            price_variation = random.uniform(0.85, 1.15)
            adjusted_price = round(unit_price * price_variation, 2)

            record = {
                "transaction_id": cls.generate_transaction_id(),
                "product_name": product_name,
                "category": category,
                "quantity": random.randint(1, 10),
                "unit_price": adjusted_price,
                "sale_date": base_date,
                "sale_time": f"{random.randint(8, 22):02d}:{random.randint(0, 59):02d}:00",
                "customer_id": cls.generate_customer_id(),
                "region": random.choice(cls.REGIONS),
            }
            records.append(record)

        return records


def insert_sales_data(records):
    """Insert sales records into the database."""
    try:
        conn = sqlite3.connect(config.DB_FILE)
        cursor = conn.cursor()

        # Insert records one by one (SQLite doesn't have COPY like PostgreSQL)
        insert_query = """
        INSERT INTO raw_sales 
        (transaction_id, product_name, category, quantity, unit_price, 
         sale_date, sale_time, customer_id, region)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        inserted = 0
        for record in records:
            try:
                cursor.execute(insert_query, (
                    record["transaction_id"],
                    record["product_name"],
                    record["category"],
                    record["quantity"],
                    record["unit_price"],
                    record["sale_date"],
                    record["sale_time"],
                    record["customer_id"],
                    record["region"]
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Skip duplicate transaction IDs
                pass

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✓ Inserted {inserted} records into 'raw_sales' table.")
        return inserted

    except Exception as e:
        print(f"✗ Error inserting data: {e}")
        return 0


def main():
    """Main execution function."""
    print("\n" + "="*50)
    print("GENERATING SAMPLE SALES DATA (SQLite)")
    print("="*50 + "\n")

    # Generate records
    print(f"Generating {config.DATA_GENERATION_COUNT} sample records...")
    records = SalesDataGenerator.generate_sales_records(config.DATA_GENERATION_COUNT)

    # Insert into database
    print("Inserting into database...")
    inserted = insert_sales_data(records)

    print("\n" + "="*50)
    print(f"✓ DATA GENERATION COMPLETE!")
    print("="*50)
    print(f"Records generated: {len(records)}")
    print(f"Records inserted: {inserted}")
    print("="*50 + "\n")
    print("✓ Next step: Run '03_etl_pipeline.py' to process and load data")


if __name__ == "__main__":
    main()