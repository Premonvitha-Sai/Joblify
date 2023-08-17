import streamlit as st
import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# Fetch data
cursor.execute("SELECT * FROM detail")
data = cursor.fetchall()
columns = [description[0] for description in cursor.description]  # Get column names

# Display data in Streamlit
st.dataframe(pd.DataFrame(data, columns=columns))

conn.close()
