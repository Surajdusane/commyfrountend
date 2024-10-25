import streamlit as st
import pandas as pd
from client.supabase import supabase
from datetime import datetime
import os

# Set page config
st.set_page_config(page_title="Docs Automation")
st.title("Upload File")
st.sidebar.success("Select the page above")

# Password protection
password = st.secrets["general"]["password"]
user_input = st.text_input("Enter password", type="password")

if user_input != password:
    st.error("Invalid password")
    st.stop()

# File upload section
uploaded_file = st.file_uploader("Upload File", type="csv")

# Link to example file
st.download_button("Example File", data=open("Example.csv", "rb").read(), file_name="Example.csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df, use_container_width=True)

    if st.button("Add to Supabase"):
        data_to_insert = []
        for index, row in df.iterrows():
            data = {
                "link": row["Links"],
                "comment_text": row["Comments"],
                "is_executed": False,
                "created_at": datetime.now().isoformat()
            }
            data_to_insert.append(data)

        # Perform bulk insert
        response = supabase.table("tasks").insert(data_to_insert).execute()

        if response:  # Check if the insert was successful
            st.success(f"Successfully added {len(data_to_insert)} rows to Supabase.")
        else:
            st.error(f"Error adding rows. Status: {response.status_code}, Error: {response.error}")
