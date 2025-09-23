import streamlit as st
import pandas as pd
import sqlite3
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Transaction Viewer",
    page_icon="💰",
    layout="wide"
)

# --- Database Connection & Data Loading ---
DB_FILE = 'transactions.db'

@st.cache_data
def load_data():
    """
    Loads transaction data from the SQLite database.
    Returns a pandas DataFrame.
    Caches the data to avoid reloading on every interaction.
    """
    if not os.path.exists(DB_FILE):
        return pd.DataFrame() # Return empty dataframe if DB doesn't exist

    try:
        conn = sqlite3.connect(DB_FILE)
        # Order by date descending to show most recent transactions first
        query = "SELECT transaction_date, description, debit_amount, credit_amount, balance FROM transactions ORDER BY transaction_date DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # --- Data Type Conversion ---
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        numeric_cols = ['debit_amount', 'credit_amount', 'balance']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return pd.DataFrame()

# --- Main Application ---
st.title("🏦 Bank Transaction Dashboard")
st.markdown("View and filter your transaction history.")

df = load_data()

if df.empty:
    st.warning("No transactions found. Please run the `app.py` script to upload a bank statement first.")
else:
    # --- Sidebar for Filters ---
    st.sidebar.header("🔍 Filter Options")

    # -- Date Range Filter --
    st.sidebar.subheader("Date Range")
    min_date = df['transaction_date'].min().date()
    max_date = df['transaction_date'].max().date()
    
    start_date = st.sidebar.date_input("From", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("To", max_date, min_value=min_date, max_value=max_date)
    
    # -- Amount Filters --
    st.sidebar.subheader("Amount")
    
    # Select Debit or Credit
    amount_type = st.sidebar.selectbox("Transaction Type", ["All", "Credit", "Debit"])
    
    # Select filter condition
    filter_condition = st.sidebar.selectbox(
        "Condition", 
        ["Any Amount", "Greater Than", "Less Than", "Between"]
    )

    amount1 = 0
    amount2 = 0

    if filter_condition == "Greater Than" or filter_condition == "Less Than":
        amount1 = st.sidebar.number_input(f"Amount", min_value=0.0, step=100.0)
    elif filter_condition == "Between":
        amount1 = st.sidebar.number_input("From Amount", min_value=0.0, step=100.0)
        amount2 = st.sidebar.number_input("To Amount", min_value=0.0, value=1000.0, step=100.0)

    # --- Filtering Logic ---
    # Start with a copy of the original dataframe
    filtered_df = df.copy()

    # Apply date filter
    filtered_df = filtered_df[
        (filtered_df['transaction_date'].dt.date >= start_date) &
        (filtered_df['transaction_date'].dt.date <= end_date)
    ]

    # Apply amount filters
    target_column = ''
    if amount_type == 'Credit':
        target_column = 'credit_amount'
    elif amount_type == 'Debit':
        target_column = 'debit_amount'

    if target_column and filter_condition != "Any Amount":
        if filter_condition == "Greater Than":
            filtered_df = filtered_df[filtered_df[target_column] > amount1]
        elif filter_condition == "Less Than":
            filtered_df = filtered_df[filtered_df[target_column] < amount1]
        elif filter_condition == "Between":
            if amount1 > amount2: # Swap if user enters amounts in wrong order
                amount1, amount2 = amount2, amount1
            filtered_df = filtered_df[filtered_df[target_column].between(amount1, amount2)]


    # --- Display Metrics and Data ---
    st.header("Filtered Transactions")

    # -- Key Metrics --
    total_credit = filtered_df['credit_amount'].sum()
    total_debit = filtered_df['debit_amount'].sum()
    net_flow = total_credit - total_debit
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Credit", f"₹{total_credit:,.2f}", delta_color="normal")
    col2.metric("Total Debit", f"₹{total_debit:,.2f}", delta_color="inverse")
    col3.metric("Net Flow", f"₹{net_flow:,.2f}", delta=f"{net_flow:,.2f}")

    # -- Display Data Table --
    st.dataframe(
        filtered_df.style.format({
            'credit_amount': '₹{:,.2f}',
            'debit_amount': '₹{:,.2f}',
            'balance': '₹{:,.2f}'
        }),
        use_container_width=True
    )
    
    st.info(f"Showing {len(filtered_df)} of {len(df)} total transactions.")
