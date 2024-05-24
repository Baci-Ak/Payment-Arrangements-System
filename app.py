
import streamlit as st
import pandas as pd

# Load the data
processed_data = pd.read_excel("data/Processed_Data.xlsx")
payment_schedule = pd.read_excel("data/Payment_Schedule.xlsx")

st.title("Payment Arrangements System Replication")

st.header("Processed Data")
st.write(processed_data)

st.header("Payment Schedule")
st.write(payment_schedule)

# Download processed data
st.header("Download Processed Data")
csv = processed_data.to_csv(index=False)
st.download_button(
    label="Download Processed Data as CSV",
    data=csv,
    file_name='Processed_Data.csv',
    mime='text/csv',
)

# Download payment schedule
st.header("Download Payment Schedule")
csv = payment_schedule.to_csv(index=False)
st.download_button(
    label="Download Payment Schedule as CSV",
    data=csv,
    file_name='Payment_Schedule.csv',
    mime='text/csv',
)
