import streamlit as st
import pandas as pd
from client.supabase import supabase
from datetime import datetime, timedelta
import os

# Password protection
password = st.secrets["general"]["password"]
user_input = st.text_input("Enter password", type="password")

if user_input != password:
    st.error("Invalid password")
    st.stop()


# Function to fetch data from Supabase
def fetch_tasks():
    response = supabase.table("tasks").select("*").execute()
    return pd.DataFrame(response.data)

def fetch_sessions():
    response = supabase.table("session_id").select("*").execute()
    return pd.DataFrame(response.data)

# Load data
tasks = fetch_tasks()
sessions = fetch_sessions()

# Convert datetime columns to pandas datetime
tasks['execution_time'] = pd.to_datetime(tasks['execution_time'])
sessions['last_used'] = pd.to_datetime(sessions['last_used'])

# Today's date
today = datetime.now()

# Task statistics
def get_comment_stats(tasks):
    executed_today = tasks[tasks['is_executed'] == True].loc[
        tasks['execution_time'].dt.date == today.date()
    ].shape[0]

    last_7_days = tasks[tasks['is_executed'] == True].loc[
        tasks['execution_time'].dt.date >= (today - timedelta(days=7)).date()
    ].shape[0]

    last_month = tasks[tasks['is_executed'] == True].loc[
        tasks['execution_time'].dt.date >= (today - timedelta(days=30)).date()
    ].shape[0]

    return executed_today, last_7_days, last_month

executed_today, last_7_days, last_month = get_comment_stats(tasks)

# Streamlit layout
st.title("Dashboard")

# Comment statistics
st.header("Comment Statistics")
st.write(f"Executed Comments Today: {executed_today}")
st.write(f"Executed Comments Last 7 Days: {last_7_days}")
st.write(f"Executed Comments Last Month: {last_month}")

# Session statistics
def get_session_stats(sessions):
    today_accounts = sessions[sessions['last_used'].dt.date == today.date()]
    total_accounts = len(sessions)

    accounts_last_used = []
    for index, row in today_accounts.iterrows():
        last_used_diff = (today - row['last_used']).total_seconds()
        accounts_last_used.append({
            'name': row['name'],
            'total_use': row['total_use'],
            'last_used_seconds': last_used_diff,
            'last_used': True  # Flag for today's usage
        })

    # Include all accounts with a flag for last used
    for index, row in sessions.iterrows():
        if row['name'] not in [acc['name'] for acc in accounts_last_used]:
            last_used_diff = (today - row['last_used']).total_seconds()
            accounts_last_used.append({
                'name': row['name'],
                'total_use': row['total_use'],
                'last_used_seconds': last_used_diff,
                'last_used': False  # Flag for not used today
            })

    return total_accounts, accounts_last_used

total_accounts, accounts_last_used = get_session_stats(sessions)

# Create a DataFrame for accounts last used
if accounts_last_used:
    # Convert to DataFrame for display
    accounts_df = pd.DataFrame(accounts_last_used)

    # Handle NaN values for last_used_seconds
    accounts_df['last_used_seconds'] = accounts_df['last_used_seconds'].fillna(0)

    # Format the last used time
    accounts_df['last_used_time'] = accounts_df['last_used_seconds'].apply(
        lambda x: f"{int(x)} seconds ago" if x < 60 else
        f"{int(x // 60)} minutes ago" if x < 3600 else
        f"{int(x // 3600)} hours ago"
    )
    
    # Add a column to indicate if the account was used today
    accounts_df['used_today'] = accounts_df['last_used'].apply(lambda x: "Yes" if x else "No")

    # Extract today's usage from the total_use column
    today_date_key = str(datetime.today().date())
    accounts_df['today_usage'] = accounts_df['total_use'].apply(
        lambda x: x.get(today_date_key, float('nan')) if isinstance(x, dict) else float('nan')
    )
    st.header("Account Statistics")
    # Display the DataFrame
    st.dataframe(accounts_df[['name', 'last_used_time', 'used_today', 'today_usage']])
else:
    st.write("No accounts have been used today.")
