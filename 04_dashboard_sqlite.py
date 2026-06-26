#!/usr/bin/env python3
"""
04_dashboard.py (SQLite Version)
Streamlit dashboard for visualizing sales data and daily summaries.
Run with: streamlit run 04_dashboard.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import config_sqlite as config
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Daily Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)


def get_db_connection():
    """Get fresh database connection for this thread."""
    try:
        conn = sqlite3.connect(config.DB_FILE, check_same_thread=False)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_daily_summary(date=None):
    """Fetch daily summary data."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        if date is None:
            date = datetime.now().date()

        query = f"""
        SELECT * FROM daily_summary
        WHERE summary_date = '{date}'
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching summary: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def fetch_sales_by_category(days=30):
    """Fetch sales data by category for the last N days."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = f"""
        SELECT 
            category,
            date(sale_date) as sale_date,
            ROUND(SUM(total_amount), 2) as total_sales,
            COUNT(*) as transaction_count,
            SUM(quantity) as total_quantity
        FROM processed_sales
        WHERE date(sale_date) >= date('now', '-{days} days')
        GROUP BY category, date(sale_date)
        ORDER BY sale_date DESC, total_sales DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching category data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def fetch_sales_by_region(days=30):
    """Fetch sales data by region for the last N days."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = f"""
        SELECT 
            region,
            date(sale_date) as sale_date,
            ROUND(SUM(total_amount), 2) as total_sales,
            COUNT(*) as transaction_count
        FROM processed_sales
        WHERE date(sale_date) >= date('now', '-{days} days')
        GROUP BY region, date(sale_date)
        ORDER BY sale_date DESC, total_sales DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching region data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def fetch_top_products(limit=10, days=30):
    """Fetch top products by sales."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = f"""
        SELECT 
            product_name,
            category,
            ROUND(SUM(total_amount), 2) as total_sales,
            SUM(quantity) as total_quantity,
            COUNT(*) as transaction_count,
            ROUND(AVG(total_amount), 2) as avg_price
        FROM processed_sales
        WHERE date(sale_date) >= date('now', '-{days} days')
        GROUP BY product_name, category
        ORDER BY total_sales DESC
        LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching product data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def fetch_time_series_sales(days=30):
    """Fetch daily sales time series."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = f"""
        SELECT 
            date(sale_date) as date,
            ROUND(SUM(total_amount), 2) as total_sales,
            COUNT(*) as transaction_count,
            SUM(quantity) as total_quantity
        FROM processed_sales
        WHERE date(sale_date) >= date('now', '-{days} days')
        GROUP BY date(sale_date)
        ORDER BY date ASC
        """
        df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error fetching time series: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def display_header():
    """Display dashboard header."""
    st.title("📊 Daily Sales Dashboard (SQLite)")
    st.markdown("---")


def display_kpis():
    """Display key performance indicators."""
    st.subheader("Today's Key Metrics")

    summary = fetch_daily_summary()

    if summary.empty:
        st.info("No data available for today yet. Run the pipeline first: python 03_etl_pipeline_sqlite.py")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Sales",
            f"${summary['total_sales'].values[0]:,.2f}",
            delta=None
        )

    with col2:
        st.metric(
            "Transactions",
            f"{int(summary['transaction_count'].values[0]):,}",
            delta=None
        )

    with col3:
        st.metric(
            "Avg Transaction",
            f"${summary['average_transaction_value'].values[0]:,.2f}",
            delta=None
        )

    with col4:
        st.metric(
            "Total Quantity",
            f"{int(summary['total_quantity'].values[0]):,}",
            delta=None
        )

    # Additional info
    col5, col6 = st.columns(2)
    with col5:
        st.metric("Top Category", summary['top_category'].values[0] or "N/A")
    with col6:
        st.metric("Top Region", summary['top_region'].values[0] or "N/A")


def display_charts():
    """Display visualization charts."""
    st.subheader("Sales Analysis")

    # Time series chart
    st.markdown("### 📈 Sales Trend (Last 30 Days)")
    ts_data = fetch_time_series_sales(days=30)

    if not ts_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ts_data['date'],
            y=ts_data['total_sales'],
            mode='lines+markers',
            name='Total Sales',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="Daily Sales Over Time",
            xaxis_title="Date",
            yaxis_title="Sales ($)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available for the selected period.")

    # Category and Region charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Sales by Category")
        category_data = fetch_sales_by_category(days=30)
        if not category_data.empty:
            category_summary = category_data.groupby('category').agg({
                'total_sales': 'sum'
            }).sort_values('total_sales', ascending=False)

            fig = px.pie(
                category_summary,
                values='total_sales',
                names=category_summary.index,
                hole=0.3,
                title="Category Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available.")

    with col2:
        st.markdown("### 🌍 Sales by Region")
        region_data = fetch_sales_by_region(days=30)
        if not region_data.empty:
            region_summary = region_data.groupby('region').agg({
                'total_sales': 'sum'
            }).sort_values('total_sales', ascending=False)

            fig = px.bar(
                region_summary,
                y='total_sales',
                title="Region Performance",
                labels={'total_sales': 'Sales ($)', 'region': 'Region'},
                color='total_sales',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No region data available.")


def display_top_products():
    """Display top products table."""
    st.subheader("🏅 Top Products")

    top_products = fetch_top_products(limit=10, days=30)

    if not top_products.empty:
        # Format for display
        display_df = top_products.copy()
        display_df['Total Sales'] = display_df['total_sales'].apply(lambda x: f"${x:,.2f}")
        display_df['Qty Sold'] = display_df['total_quantity'].apply(lambda x: f"{x:,.0f}")
        display_df['Transactions'] = display_df['transaction_count'].apply(lambda x: f"{x:,.0f}")
        display_df['Avg Price'] = display_df['avg_price'].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            display_df[['product_name', 'category', 'Total Sales', 'Qty Sold', 'Transactions', 'Avg Price']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No product data available.")


def display_sidebar():
    """Display sidebar options."""
    st.sidebar.title("⚙️ Settings")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 About This Dashboard")
    st.sidebar.markdown("""
    **Daily Sales Pipeline Dashboard (SQLite)**

    - Real-time sales metrics
    - Category & region analysis
    - Product performance tracking
    - Automated daily updates

    Data refreshes every 60 seconds.
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    **Database Info:**

    - Database: `{config.DB_FILE}` 
    - Type: `SQLite`
    - Last Updated: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
    """)


def main():
    """Main dashboard function."""
    display_sidebar()
    display_header()
    display_kpis()
    st.markdown("---")
    display_charts()
    st.markdown("---")
    display_top_products()

    # Auto-refresh message
    st.markdown(f"""
    ---
    <div style="text-align: center; color: gray; font-size: 12px;">
    Dashboard auto-refreshes every 60 seconds | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()