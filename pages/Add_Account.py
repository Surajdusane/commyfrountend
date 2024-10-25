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


def add_or_update_session(account_name, session_id):
    data = {
        "name": account_name,
        "session_id": session_id,
    }
    # Use upsert with the specified unique key
    response = supabase.table('session_id').upsert(data, on_conflict=['name']).execute()

    return f"Account added or updated"

st.title("Add or Update Session")

account_name = st.text_input("Account Name")
session_id = st.text_input("Session ID")

if st.button("Add or Update Session"):
    if account_name and session_id:
        result = add_or_update_session(account_name, session_id)
        st.success(result)  # Display the result
    else:
        st.error("Please fill in all fields.")
