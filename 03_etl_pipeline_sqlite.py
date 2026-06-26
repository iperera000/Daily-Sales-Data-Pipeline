#!/usr/bin/env python3
"""
03_etl_pipeline.py (SQLite Version)
Main ETL pipeline: Extract raw sales data, Transform (clean, enrich),
Load into processed_sales and calculate daily_summary.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import config_sqlite as config
import time


class ETLPipeline:
    """Main ETL Pipeline for SQLite."""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.start_time = None
        self.records_processed = 0
        self.records_inserted = 0
        self.error_message = None

    def connect_db(self):
        """Connect to SQLite database."""
        try:
            self.conn = sqlite3.connect(config.DB_FILE)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            self.error_message = f"Connection failed: {str(e)}"
            print(f"✗ {self.error_message}")
            return False

    def close_db(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def extract_raw_data(self):
        """Extract raw sales data from raw_sales table."""
        try:
            query = """
            SELECT transaction_id, product_name, category, quantity, unit_price,
                   sale_date, sale_time, customer_id, region
            FROM raw_sales
            WHERE sale_date = date('now')
            ORDER BY rowid DESC
            LIMIT 1000;
            """
            df = pd.read_sql_query(query, self.conn)
            self.records_processed = len(df)
            print(f"✓ Extracted {self.records_processed} raw records.")
            return df

        except Exception as e:
            self.error_message = f"Extract failed: {str(e)}"
            print(f"✗ {self.error_message}")
            return pd.DataFrame()

    def transform_data(self, df):
        """Transform and clean the data."""
        try:
            if df.empty:
                print("⚠ No data to transform.")
                return df

            original_count = len(df)

            # Convert data types
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
            df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0)
            df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date

            # Calculate total amount
            df['total_amount'] = (df['quantity'] * df['unit_price']).round(2)

            # Remove invalid records (negative prices, zero quantity)
            df = df[(df['quantity'] > 0) & (df['unit_price'] > 0)]

            # Remove duplicates based on transaction_id
            df = df.drop_duplicates(subset=['transaction_id'], keep='first')

            # Fill missing values
            df['product_name'] = df['product_name'].fillna('Unknown Product')
            df['category'] = df['category'].fillna('Other')
            df['region'] = df['region'].fillna('Unknown')
            df['customer_id'] = df['customer_id'].fillna('CUST-00000')

            # Validate data
            df = df[
                (df['quantity'] > 0) &
                (df['unit_price'] > 0) &
                (df['total_amount'] > 0) &
                (df['product_name'].notna()) &
                (df['transaction_id'].notna())
                ]

            removed_count = original_count - len(df)
            if removed_count > 0:
                print(f"⚠ Removed {removed_count} invalid records during transformation.")

            print(f"✓ Transformed {len(df)} records (valid data).")
            return df

        except Exception as e:
            self.error_message = f"Transform failed: {str(e)}"
            print(f"✗ {self.error_message}")
            return df

    def load_processed_data(self, df):
        """Load processed data into processed_sales table."""
        try:
            if df.empty:
                print("⚠ No data to load.")
                return 0

            insert_query = """
            INSERT OR IGNORE INTO processed_sales 
            (transaction_id, product_name, category, quantity, unit_price, 
             total_amount, sale_date, sale_time, customer_id, region)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            for idx, row in df.iterrows():
                self.cursor.execute(insert_query, (
                    row['transaction_id'],
                    row['product_name'],
                    row['category'],
                    row['quantity'],
                    row['unit_price'],
                    row['total_amount'],
                    row['sale_date'],
                    row['sale_time'],
                    row['customer_id'],
                    row['region']
                ))

            self.conn.commit()
            self.records_inserted = len(df)
            print(f"✓ Loaded {self.records_inserted} records into 'processed_sales'.")
            return self.records_inserted

        except Exception as e:
            self.error_message = f"Load failed: {str(e)}"
            print(f"✗ {self.error_message}")
            self.conn.rollback()
            return 0

    def generate_daily_summary(self):
        """Generate daily summary from processed sales data."""
        try:
            # Get today's summary
            summary_query = """
            SELECT
                date('now') as summary_date,
                ROUND(SUM(total_amount), 2) as total_sales,
                SUM(quantity) as total_quantity,
                COUNT(*) as transaction_count,
                ROUND(AVG(total_amount), 2) as average_transaction_value
            FROM processed_sales
            WHERE date(sale_date) = date('now')
            """

            self.cursor.execute(summary_query)
            result = self.cursor.fetchone()

            if result:
                summary_date = result[0]
                total_sales = result[1]
                total_quantity = result[2]
                transaction_count = result[3]
                average_transaction_value = result[4]

                # Get top category
                self.cursor.execute("""
                    SELECT category FROM processed_sales 
                    WHERE date(sale_date) = date('now')
                    GROUP BY category ORDER BY SUM(total_amount) DESC LIMIT 1
                """)
                top_category_result = self.cursor.fetchone()
                top_category = top_category_result[0] if top_category_result else "Unknown"

                # Get top region
                self.cursor.execute("""
                    SELECT region FROM processed_sales 
                    WHERE date(sale_date) = date('now')
                    GROUP BY region ORDER BY SUM(total_amount) DESC LIMIT 1
                """)
                top_region_result = self.cursor.fetchone()
                top_region = top_region_result[0] if top_region_result else "Unknown"

                # Insert or update summary
                insert_summary = """
                INSERT OR REPLACE INTO daily_summary
                (summary_date, total_sales, total_quantity, transaction_count,
                 average_transaction_value, top_category, top_region, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """

                self.cursor.execute(insert_summary, (
                    summary_date,
                    total_sales,
                    total_quantity,
                    transaction_count,
                    average_transaction_value,
                    top_category,
                    top_region
                ))

                self.conn.commit()
                print("✓ Generated daily summary.")
                return True
            else:
                print("⚠ No data to summarize.")
                return True

        except Exception as e:
            self.error_message = f"Summary generation failed: {str(e)}"
            print(f"✗ {self.error_message}")
            self.conn.rollback()
            return False

    def log_pipeline_run(self, status):
        """Log pipeline execution."""
        try:
            duration = time.time() - self.start_time
            log_query = """
            INSERT INTO pipeline_log
            (status, records_processed, records_inserted, error_message, duration_seconds)
            VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(log_query, (
                status, self.records_processed, self.records_inserted,
                self.error_message, duration
            ))
            self.conn.commit()
            print(f"✓ Pipeline run logged (duration: {duration:.2f}s, status: {status}).")

        except Exception as e:
            print(f"✗ Failed to log pipeline run: {e}")

    def run(self):
        """Execute the complete ETL pipeline."""
        self.start_time = time.time()

        print("\n" + "=" * 60)
        print("STARTING ETL PIPELINE (SQLite)")
        print("=" * 60 + "\n")

        # Connect to database
        if not self.connect_db():
            self.log_pipeline_run("FAILED")
            return False

        try:
            # Extract
            print("STEP 1: EXTRACT")
            print("-" * 60)
            df_raw = self.extract_raw_data()

            if df_raw.empty:
                print("⚠ No new data to process.")
                self.close_db()
                self.log_pipeline_run("COMPLETED")
                return True

            # Transform
            print("\nSTEP 2: TRANSFORM")
            print("-" * 60)
            df_transformed = self.transform_data(df_raw)

            # Load
            print("\nSTEP 3: LOAD")
            print("-" * 60)
            self.load_processed_data(df_transformed)

            # Generate summary
            print("\nSTEP 4: GENERATE SUMMARY")
            print("-" * 60)
            self.generate_daily_summary()

            # Log success
            self.log_pipeline_run("SUCCESS")

            print("\n" + "=" * 60)
            print("✓ ETL PIPELINE COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Records processed: {self.records_processed}")
            print(f"Records inserted: {self.records_inserted}")
            print(f"Duration: {time.time() - self.start_time:.2f} seconds")
            print("=" * 60 + "\n")

            return True

        except Exception as e:
            self.error_message = str(e)
            self.log_pipeline_run("FAILED")
            print(f"\n✗ Pipeline failed: {e}")
            return False

        finally:
            self.close_db()


def main():
    """Main execution function."""
    pipeline = ETLPipeline()
    success = pipeline.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())