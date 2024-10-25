from datetime import datetime, timedelta
from client.supabase import supabase
import pandas as pd
import streamlit as st
import os

# Password protection
password = st.secrets["general"]["password"]
user_input = st.text_input("Enter password", type="password")

if user_input != password:
    st.error("Invalid password")
    st.stop()


def get_data_from_last_days(days):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    response = supabase.table('tasks').select('*').gt('created_at', start_time.isoformat()).execute()
    return response.data

def get_data_from_custom_range(start_date, end_date):
    response = supabase.table('tasks').select('*').gte('created_at', start_date).lte('created_at', end_date).execute()
    return response.data

st.title("Data Querying with Supabase")

# Initialize an empty DataFrame
data_df = pd.DataFrame()

# Buttons for preset time ranges
if st.button('Last 24 Hours'):
    data = get_data_from_last_days(1)
    data_df = pd.DataFrame(data)
    st.write(data_df)

if st.button('Last 7 Days'):
    data = get_data_from_last_days(7)
    data_df = pd.DataFrame(data)
    st.write(data_df)

if st.button('Last Month'):
    data = get_data_from_last_days(30)
    data_df = pd.DataFrame(data)
    st.write(data_df)

# Custom date range
st.subheader("Custom Date Range")
start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
end_date = st.date_input("End Date", value=datetime.now())

if st.button('Get Custom Range Data'):
    start_date_time = datetime.combine(start_date, datetime.min.time())
    end_date_time = datetime.combine(end_date, datetime.max.time())
    data = get_data_from_custom_range(start_date_time.isoformat(), end_date_time.isoformat())
    data_df = pd.DataFrame(data)
    st.write(data_df)

# Export option
if not data_df.empty:
    st.subheader("Export Data")
    csv = data_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='tasks_data.csv',
        mime='text/csv'
    )
