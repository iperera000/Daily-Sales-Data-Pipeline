#!/usr/bin/env python3
"""
01_setup_database.py (SQLite Version)
Creates SQLite database and tables for the daily sales pipeline.
Run this ONCE before starting the pipeline.
No PostgreSQL or psycopg2 needed - uses SQLite (built into Python).
"""

import sqlite3
import os
from datetime import datetime

# Database file path
DB_FILE = "sales_pipeline.db"

def create_database():
    """Create SQLite database file."""
    try:
        # This automatically creates the file if it doesn't exist
        conn = sqlite3.connect(DB_FILE)
        conn.close()
        print(f"✓ Database file '{DB_FILE}' created/verified.")
        return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False


def create_tables():
    """Create tables in the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # ===== RAW SALES TABLE =====
        create_raw_sales = """
        CREATE TABLE IF NOT EXISTS raw_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            sale_date DATE NOT NULL,
            sale_time TIME NOT NULL,
            customer_id TEXT NOT NULL,
            region TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_raw_sales)
        print("✓ Created 'raw_sales' table.")

        # ===== PROCESSED SALES TABLE =====
        create_processed_sales = """
        CREATE TABLE IF NOT EXISTS processed_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            sale_date DATE NOT NULL,
            sale_time TIME NOT NULL,
            customer_id TEXT NOT NULL,
            region TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_processed_sales)
        print("✓ Created 'processed_sales' table.")

        # ===== DAILY SUMMARY TABLE =====
        create_daily_summary = """
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date DATE UNIQUE NOT NULL,
            total_sales REAL,
            total_quantity INTEGER,
            transaction_count INTEGER,
            average_transaction_value REAL,
            top_category TEXT,
            top_region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_daily_summary)
        print("✓ Created 'daily_summary' table.")

        # ===== PIPELINE LOG TABLE =====
        create_pipeline_log = """
        CREATE TABLE IF NOT EXISTS pipeline_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            records_processed INTEGER,
            records_inserted INTEGER,
            error_message TEXT,
            duration_seconds REAL
        );
        """
        cursor.execute(create_pipeline_log)
        print("✓ Created 'pipeline_log' table.")

        # Create indexes for better query performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_raw_sales_date ON raw_sales(sale_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_processed_sales_date ON processed_sales(sale_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_summary(summary_date)"
        )
        print("✓ Created database indexes.")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "="*50)
        print("✓ DATABASE SETUP COMPLETE!")
        print("="*50)
        print(f"Database file: {DB_FILE}")
        print(f"Database type: SQLite")
        print(f"Tables created:")
        print(f"  • raw_sales")
        print(f"  • processed_sales")
        print(f"  • daily_summary")
        print(f"  • pipeline_log")
        print("="*50 + "\n")
        return True

    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def verify_tables():
    """Verify all tables were created successfully."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]

        print("\n" + "="*50)
        print("✓ VERIFICATION")
        print("="*50)
        print(f"Tables found: {len(table_names)}")
        for table_name in table_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table_name}: {count} records")
        print("="*50 + "\n")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


def main():
    """Main execution function."""
    print("\n" + "="*50)
    print("INITIALIZING DATABASE SETUP (SQLite)")
    print("="*50 + "\n")

    # Create database file
    if not create_database():
        return False

    # Create tables
    if not create_tables():
        return False

    # Verify
    if not verify_tables():
        return False

    print("✓ Next step: Run '02_data_generator.py' to create sample data\n")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)