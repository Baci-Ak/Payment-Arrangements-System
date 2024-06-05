
import streamlit as st
import pandas as pd
from PIL import Image
import datetime

# Initialize session state variables
if 'date_format' not in st.session_state:
    st.session_state['date_format'] = '%Y-%m-%d'
if 'currency_symbol' not in st.session_state:
    st.session_state['currency_symbol'] = '$'

# Setting page config to wide mode for better mobile experience
st.set_page_config(page_title="Payment Arrangement System", layout="wide")

# Title and logo
st.title("Payment Arrangement System")
#image = Image.open('profile_photo.png')
#st.image(image, caption='Baci Akom', width=100, use_column_width=True)

# Sidebar for navigation and settings
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("", ["Home", "Settings", "Help"], format_func=lambda x: "Menu" if x == "" else x)

if app_mode == "Settings":
    st.sidebar.subheader("Custom Settings")
    date_formats = {'YYYY-MM-DD': '%Y-%m-%d', 'DD-MM-YYYY': '%d-%m-%Y', 'MM-DD-YYYY': '%m-%d-%Y'}
    selected_date_format = st.sidebar.selectbox('Date Format', list(date_formats.keys()))
    st.session_state['date_format'] = date_formats[selected_date_format]
    st.session_state['currency_symbol'] = st.sidebar.text_input("Currency Symbol", value=st.session_state['currency_symbol'])

if app_mode == "Help":
    st.sidebar.subheader("Help Section")
    st.markdown("""
    ### FAQ
    - **How to upload data:** Go to the Home section and use the file uploader.
    - **How to process data:** After uploading, click on 'Process Uploaded Data'.
    - **How to see settings:** Navigate to the Settings tab in the sidebar.
    """)

if app_mode == "Home":
    # Description of the system
    st.markdown("""
    This system manages the functionality of a payment arrangements system used by financial services companies.
    It calculates all planned payments, including the last payment date and amount, for each customer based on the provided data.
    Users can upload a CSV file with payment arrangement details, and the system will process this data to generate a detailed payment schedule
    and display it alongside the original and processed data.
    Please ensure your CSV file contains the following columns:
    - `CustomerReference`: Unique identifier for each customer
    - `FirstPaymentDate`: The date of the first payment (format: YYYY-MM-DD)
    - `Frequency`: Payment frequency ('single', 'monthly', 'weekly', 'daily')
    - `FrequencyType`: Type of frequency ('M', 'W', 'D' for monthly, weekly, daily)
    - `FrequencyNumber`: Number of frequency intervals between payments
    - `NumberOfPayments`: Total number of payments
    - `TotalToPay`: Total amount to be paid
    - `InstalmentAmount`: Amount of each instalment
    """)

    # Function to calculate payment dates based on given frequency and number of payments
    def calculate_payment_dates(start_date, frequency, freq_type, freq_number, num_payments):
        dates = []
        if frequency == "single":
            dates = [start_date]
        elif frequency == "monthly" and freq_type == "M":
            for i in range(num_payments):
                dates.append(start_date + datetime.timedelta(days=30*i*freq_number))  # Approximation for monthly
        elif frequency == "weekly" and freq_type == "W":
            for i in range(num_payments):
                dates.append(start_date + datetime.timedelta(days=7*i*freq_number))
        elif frequency == "daily" and freq_type == "D":
            for i in range(num_payments):
                dates.append(start_date + datetime.timedelta(days=i*freq_number))
        return dates

    # File uploader for data
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    process_button = st.button("Process Uploaded Data")
    
    if uploaded_file and process_button:
        data = pd.read_csv(uploaded_file)
        # Validate required columns
        required_columns = ['CustomerReference', 'FirstPaymentDate', 'Frequency', 'FrequencyType', 'FrequencyNumber', 'NumberOfPayments', 'TotalToPay', 'InstalmentAmount']
        if not all(column in data.columns for column in required_columns):
            st.error("Uploaded file does not contain the required columns. Please check the data format and try again.")
        else:
            data['FirstPaymentDate'] = pd.to_datetime(data['FirstPaymentDate'], format=st.session_state['date_format'], errors='coerce')
            if data['FirstPaymentDate'].isna().any():
                st.error("Some 'FirstPaymentDate' entries are invalid. Please correct the dates and try again.")
            else:
                data['PaymentDates'] = data.apply(lambda row: calculate_payment_dates(
                    row['FirstPaymentDate'], row['Frequency'], row['FrequencyType'],
                    row['FrequencyNumber'], row['NumberOfPayments']
                ), axis=1)
                data['LastPaymentDate'] = data['PaymentDates'].apply(lambda x: x[-1] if len(x) > 0 else None)
                data['LastPaymentAmount'] = data.apply(lambda row: row['TotalToPay'] - row['InstalmentAmount'] * (row['NumberOfPayments'] - 1), axis=1)

                # Explode payment dates for a detailed schedule
                payment_schedule = data[['CustomerReference', 'PaymentDates', 'InstalmentAmount']].explode('PaymentDates')
                payment_schedule.rename(columns={'PaymentDates': 'PaymentDate', 'InstalmentAmount': 'PaymentAmount'}, inplace=True)

                # Display the uploaded, processed, and payment schedule data
                st.subheader("Uploaded Data")
                st.write(data)
                st.subheader("Processed Data")
                st.write(data)
                st.subheader("Payment Schedule")
                st.write(payment_schedule)

    else:
        # Load the default data
        default_processed_data = pd.read_excel("data/Processed_Data.xlsx")
        default_payment_schedule = pd.read_excel("data/Payment_Schedule.xlsx")
        default_original_data = pd.read_csv("data/CaseStudy Data.csv")
        
        # Display the default data
        st.subheader("Default Processed Data")
        st.write(default_processed_data)
        st.subheader("Default Payment Schedule")
        st.write(default_payment_schedule)
        st.subheader("Default Original Data")
        st.write(default_original_data)

# Footer
st.markdown("Developed by Bassey Akom")
st.markdown("Contact: [baciakom](https://www.linkedin.com/in/basseyakom/)")
st.markdown("Source code: [GitHub](https://github.com/Baci-Ak/Payment-Arrangements-System/tree/main)")
st.markdown("Report issues: [GitHub](https://github.com/Baci-Ak/Payment-Arrangements-System/issues)")
st.markdown("Acknowledgements: [RStudio](https://rstudio.com/)")


