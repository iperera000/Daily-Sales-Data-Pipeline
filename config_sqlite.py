import os

# ===== DATABASE CONFIGURATION (SQLite) =====
DB_FILE = "sales_pipeline.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# ===== PIPELINE CONFIGURATION =====
DATA_GENERATION_COUNT = 100
BATCH_SIZE = 50

# ===== FILE PATHS =====
DATA_FILE = "sales_data_raw.csv"
PROCESSED_DATA_FILE = "sales_data_processed.csv"
LOGS_DIR = "logs"

# ===== SCHEDULING =====
PIPELINE_RUN_TIME = "14:30"

# Create logs directory if it doesn't exist
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

print(f"✓ Configuration loaded: SQLite database = {DB_FILE}")