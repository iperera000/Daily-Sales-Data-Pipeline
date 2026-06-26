# 📊 Daily Sales Data Pipeline

A complete **end-to-end data pipeline system** that generates, processes, and visualizes daily sales data. Built with Python, SQLite, Pandas, and Streamlit.


---

## 🎯 Overview

This project demonstrates a **production-grade data pipeline** that:
- **Generates** realistic sample sales data
- **Processes** raw data with ETL (Extract, Transform, Load)
- **Stores** processed data in SQLite database
- **Visualizes** real-time metrics in an interactive dashboard

Perfect for learning **data engineering**, **ETL pipelines**, and **analytics dashboards**.

---

## ✨ Features

- ✅ **Data Generation**: Random yet realistic sales transactions
- ✅ **ETL Pipeline**: Extract → Transform → Load with validation
- ✅ **SQLite Database**: Lightweight, file-based, no server required
- ✅ **Real-time Dashboard**: Live metrics with Streamlit
- ✅ **Data Validation**: Automatic cleanup of invalid records
- ✅ **Performance Optimization**: Database indexes, caching, query optimization
- ✅ **Error Handling**: Comprehensive logging and error tracking
- ✅ **Daily Summaries**: Pre-calculated aggregated metrics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               DAILY SALES PIPELINE SYSTEM                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  01_SETUP.PY     │
│  Create Database │
│  & Tables        │
└────────┬─────────┘
         ↓
┌──────────────────┐     ┌────────────────────┐
│ 02_GENERATOR.PY  │────→│  raw_sales table   │
│ Generate Data    │     │  (100 records)     │
└──────────────────┘     └────────────────────┘
                                  ↓
                         ┌────────────────────┐
                         │  03_ETL.PY         │
                         │  Process Data      │
                         └────────┬───────────┘
                                  ↓
                    ┌─────────────────────────┐
                    │ processed_sales table   │
                    │ daily_summary table     │
                    │ pipeline_log table      │
                    └────────────┬────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │ 04_DASHBOARD.PY        │
                    │ Streamlit Visualization│
                    └────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │  Browser (localhost)   │
                    │  Real-time Charts      │
                    └────────────────────────┘
```

---

## 📋 Project Structure

```
sales_pipeline/
│
├── 01_setup_database.py          # Initialize SQLite database
├── 02_data_generator_sqlite.py   # Generate sample sales data
├── 03_etl_pipeline_sqlite.py     # ETL: Extract, Transform, Load
├── 04_dashboard_sqlite.py        # Streamlit dashboard
│
├── config_sqlite.py              # Configuration settings
├── requirements.txt              # Python dependencies
├── sales_pipeline.db             # SQLite database file
│
├── logs/                         # Pipeline execution logs
├── README.md                     # Project documentation
└── .gitignore                    # Git ignore file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/sales-pipeline.git
cd sales-pipeline
```

2. **Create virtual environment**
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Usage

Run the pipeline in order:

```bash
# Step 1: Setup database (run once)
python 01_setup_database.py

# Step 2: Generate sample data
python 02_data_generator_sqlite.py

# Step 3: Process data with ETL
python 03_etl_pipeline_sqlite.py

# Step 4: Launch dashboard
streamlit run 04_dashboard_sqlite.py
```

The dashboard will open at `http://localhost:8501`

---

## 📊 What You Get

### Dashboard Features

**Today's Key Metrics**
- Total Sales (sum of all transactions)
- Transaction Count (number of sales)
- Average Transaction Value
- Total Quantity Sold
- Top Category (by revenue)
- Top Region (by revenue)

**Visualizations**
- **Sales Trend Chart**: Daily sales over last 30 days
- **Category Distribution**: Pie chart of sales by category
- **Region Performance**: Bar chart of sales by region
- **Top Products Table**: Best sellers with metrics

**Auto-refresh**: Dashboard updates every 60 seconds

---

## 🔄 Pipeline Workflow

### Step 1: Data Generation (02_data_generator.py)

Generates 100 realistic sales transactions:

```
Product Catalog:
- Laptop ($899.99) [Electronics]
- Mouse ($25.50) [Electronics]
- Monitor ($299.99) [Electronics]
- T-Shirt ($19.99) [Clothing]
- Jeans ($49.99) [Clothing]
- Coffee Maker ($89.99) [Home]
... and more

Random Values:
- Quantity: 1-10 items per transaction
- Price variation: ±15% from base price (simulates discounts)
- Region: North, South, East, West, Central
- Customer ID: CUST-XXXXX (randomly generated)
- Transaction ID: TXN-XXXXXXXXXX (unique identifier)
```

**Output**: Inserts into `raw_sales` table

### Step 2: ETL Processing (03_etl_pipeline.py)

**Extract**: Query raw data from `raw_sales` table
```sql
SELECT * FROM raw_sales WHERE sale_date = TODAY
```

**Transform**: Clean and validate data
- Convert data types (int, float, datetime)
- Calculate `total_amount = quantity × unit_price`
- Remove invalid records (negative prices, zero quantities)
- Remove duplicates by transaction_id
- Fill missing values with defaults
- Validate all required fields

**Load**: Insert cleaned data into `processed_sales`

**Summarize**: Calculate daily metrics
```sql
SELECT
    SUM(total_amount) as total_sales,
    SUM(quantity) as total_quantity,
    COUNT(*) as transaction_count,
    AVG(total_amount) as average_transaction_value,
    -- Top category and region by revenue
FROM processed_sales
WHERE DATE(sale_date) = TODAY
```

### Step 3: Visualization (04_dashboard.py)

Queries `daily_summary` and `processed_sales` tables to display:
- Cached queries (60-second TTL) for performance
- Real-time charts with Plotly
- Responsive layout with Streamlit columns

---

## 🗄️ Database Schema

### raw_sales
Raw, unprocessed sales data from the data generator.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Auto-increment primary key |
| transaction_id | TEXT (UNIQUE) | Unique transaction identifier |
| product_name | TEXT | Product name (e.g., "Laptop") |
| category | TEXT | Category (Electronics, Clothing, Home) |
| quantity | INTEGER | Number of items sold |
| unit_price | REAL | Price per item |
| sale_date | DATE | Date of sale |
| sale_time | TIME | Time of sale |
| customer_id | TEXT | Customer identifier |
| region | TEXT | Geographic region |
| created_at | TIMESTAMP | Record creation timestamp |

### processed_sales
Cleaned, validated, analytics-ready data.

| Column | Type | Description |
|--------|------|-------------|
| (all from raw_sales) | | |
| total_amount | REAL | quantity × unit_price |
| processed_at | TIMESTAMP | When record was processed |

### daily_summary
Pre-calculated daily metrics for fast dashboard queries.

| Column | Type | Description |
|--------|------|-------------|
| summary_date | DATE | Date (UNIQUE) |
| total_sales | REAL | Total revenue for the day |
| total_quantity | INTEGER | Total items sold |
| transaction_count | INTEGER | Number of transactions |
| average_transaction_value | REAL | Average sale value |
| top_category | TEXT | Best-selling category |
| top_region | TEXT | Best-performing region |
| updated_at | TIMESTAMP | Last update time |

### pipeline_log
Audit trail of pipeline executions.

| Column | Type | Description |
|--------|------|-------------|
| run_date | TIMESTAMP | When pipeline ran |
| status | TEXT | SUCCESS, FAILED, etc. |
| records_processed | INTEGER | Raw records extracted |
| records_inserted | INTEGER | Records loaded |
| error_message | TEXT | Error details if failed |
| duration_seconds | REAL | Execution time |

---

## 📈 Example Output

### Generated Data
```
transaction_id  | product_name | category    | quantity | unit_price | region
────────────────┼──────────────┼─────────────┼──────────┼────────────┼────────
TXN-ABC123XY45  | Laptop       | Electronics | 2        | 979.99     | North
TXN-DEF789QW23  | T-Shirt      | Clothing    | 5        | 22.99      | South
TXN-GHI456KL78  | Monitor      | Electronics | 1        | 299.99     | East
```

### Daily Summary
```
date       | total_sales | transaction_count | avg_trans | top_category | top_region
───────────┼─────────────┼───────────────────┼───────────┼──────────────┼──────────
2024-06-26 | $45,230.75  | 127               | $356.30   | Electronics  | North
```

---

## ⚙️ Configuration

Edit `config_sqlite.py` to customize:

```python
# Database
DB_FILE = "sales_pipeline.db"                # SQLite file path
DATABASE_URL = f"sqlite:///{DB_FILE}"        # Connection string

# Pipeline
DATA_GENERATION_COUNT = 100                  # Records to generate
BATCH_SIZE = 50                              # Records per batch

# File paths
DATA_FILE = "sales_data_raw.csv"             # Raw CSV export
PROCESSED_DATA_FILE = "sales_data_processed.csv"  # Processed CSV
LOGS_DIR = "logs"                            # Log directory

# Scheduling
PIPELINE_RUN_TIME = "14:30"                  # Daily run time
```

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Activate virtual environment first
```bash
# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

# Then install
pip install -r requirements.txt
```

### Issue: SQLite Threading Error
```
"SQLite objects created in a thread can only be used in that same thread"
```

**Solution**: Already fixed in `04_dashboard_sqlite.py`
```python
def get_db_connection():
    conn = sqlite3.connect(config.DB_FILE, check_same_thread=False)
    return conn
```

### Issue: No data appears in dashboard

**Solution**: Ensure you ran the pipeline in order:
```bash
python 01_setup_database.py    # Create tables
python 02_data_generator_sqlite.py  # Generate data
python 03_etl_pipeline_sqlite.py    # Process data
streamlit run 04_dashboard_sqlite.py  # View dashboard
```

### Issue: Dashboard is slow

**Solution**: Check cache settings in `04_dashboard_sqlite.py`
```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_daily_summary():
    ...
```

Lower the TTL for more frequent updates (but slower), or increase for better performance.

---

## 📚 Learning Resources

This project teaches:

- **Python**: Pandas, SQLite3, datetime handling
- **Databases**: Schema design, normalization, indexing, SQL queries
- **ETL**: Data extraction, transformation, validation, loading
- **Data Analysis**: Aggregation, grouping, summarization
- **Web UI**: Streamlit dashboards, interactive charts with Plotly
- **Best Practices**: Error handling, logging, configuration management

---

## 🎓 Real-World Applications

This architecture is used by companies like:

- **Uber**: GPS tracking → aggregated metrics
- **Spotify**: User activity → recommendations
- **Netflix**: Watch history → trending content
- **Amazon**: Product views → sales forecasting
- **Stripe**: Transactions → financial reports

---


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---



## 🌟 Acknowledgments

- Streamlit for the amazing dashboard framework
- Pandas for data manipulation
- SQLite for lightweight database

---

