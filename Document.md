
```markdown
# Payment Arrangements System Replication - Code Explanation and Thought Process

## Introduction to the Problem

The Payment Arrangements System Replication project aims to replicate the functionality of an in-house payment arrangement system used by a credit management company. The main goal is to calculate all planned payments, including the last payment date and amount, for each customer based on the provided data.

The project uses a dataset containing anonymized arrangements for customers. The company's system uses this information to calculate all dates and payments expected from each arrangement. This project replicates that functionality using R for data processing and Streamlit for the interactive application.

## Thought Process

### Understanding the Data

The first step was to understand the structure of the provided data. The dataset contains the following columns:
- `CustomerReference`: Unique identifier for the customer.
- `TotalToPay`: Total amount to be paid by the customer.
- `FirstPayment`: Amount of the first payment.
- `FirstPaymentDate`: Date of the first payment.
- `NumberOfPayments`: Total number of payments.
- `InstalmentAmount`: Amount of each installment.
- `Frequency`: Frequency of the payments (e.g., single, monthly).
- `FrequencyType`: Type of frequency (e.g., days, weeks, months).
- `FrequencyNumber`: Number associated with the frequency type.

### Defining the Problem

The problem involves calculating payment dates based on the provided frequency and number of payments. Important details include the start date, total amount, and installment amounts. The deliverables include:
1. Calculating all planned payment dates for each arrangement.
2. Determining the last payment date and amount.
3. Documenting the thought process and solution.

### Approach

1. **Data Extraction**: The data is extracted from an on-premise SQL server.
2. **Date Calculation**: A custom function is created to generate all payment dates based on the provided frequency and number of payments.
3. **Data Processing**: The data is processed to add additional columns for payment dates, last payment date, and last payment amount.
4. **Output Generation**: The processed data and payment schedules are exported to Excel files.

## Code Explanation

### Loading Libraries

```r
# Load necessary libraries
library(readr)       # For reading CSV files
library(dplyr)       # For data manipulation
library(lubridate)   # For date manipulation
library(tidyr)       # For unnesting data
library(openxlsx)    # For writing Excel files
```

These libraries are essential for reading data, manipulating data, handling dates, and exporting to Excel.

### Reading the Data

```r
# Read the CSV file
data <- read_csv("data/CaseStudy Data.csv", show_col_types = FALSE)
```

The dataset is read from a CSV file and loaded into a data frame.

### Viewing the Data Structure

```r
# View the first few rows of the data to understand its structure
head(data)
View(data)
```

This step is to understand the structure of the data.

### Calculating Payment Dates

```r
# Function to calculate payment dates based on given frequency and number of payments
calculate_payment_dates <- function(start_date, frequency, freq_type, freq_number, num_payments) {
  dates <- c() # Initialize an empty vector to store the dates
  if (frequency == "single") {
    dates <- c(start_date) # If frequency is single, only one payment date is needed
  } else if (frequency == "monthly" && freq_type == "M") {
    for (i in 0:(num_payments-1)) {
      dates <- c(dates, start_date %m+% months(i * freq_number)) # Add monthly payment dates
    }
  } else if (frequency == "weekly" && freq_type == "W") {
    for (i in 0:(num_payments-1)) {
      dates <- c(dates, start_date + weeks(i * freq_number)) # Add weekly payment dates
    }
  } else if (frequency == "daily" && freq_type == "D") {
    for (i in 0:(num_payments-1)) {
      dates <- c(dates, start_date + days(i * freq_number)) # Add daily payment dates
    }
  }
  return(as.Date(dates, origin = "1970-01-01")) # Return dates as Date type
}
```

This function generates all payment dates based on the provided frequency and number of payments.

### Processing the Data

```r
# Process the data to calculate payment dates, last payment date, and last payment amount
processed_data <- data %>%
  rowwise() %>% # Process each row individually
  mutate(
    PaymentDates = list(calculate_payment_dates(ymd(FirstPaymentDate), Frequency, FrequencyType, FrequencyNumber, NumberOfPayments)), # Calculate payment dates
    LastPaymentDate = ifelse(length(PaymentDates) > 0, max(PaymentDates), NA), # Calculate last payment date
    LastPaymentAmount = ifelse(length(PaymentDates) > 0, TotalToPay - InstalmentAmount * (NumberOfPayments - 1), NA) # Calculate last payment amount
  ) %>%
  ungroup() # Ungroup to revert back to the original data structure
```

This step processes the data to calculate payment dates, last payment date, and last payment amount.

### Ensuring Consistency in Payment Dates

```r
# Convert all PaymentDates elements to Date type for consistency
processed_data <- processed_data %>%
  mutate(PaymentDates = lapply(PaymentDates, as.Date, origin = "1970-01-01"))
```

This ensures all payment dates are consistently of Date type.

### Unnesting and Exporting Data

```r
# Unnest the payment dates to create a flat structure
payment_schedule <- processed_data %>%
  unnest(PaymentDates) %>%
  select(CustomerReference, PaymentDates, InstalmentAmount) %>%
  rename(
    PaymentDate = PaymentDates,
    PaymentAmount = InstalmentAmount
  )

# Export the payment schedule to an Excel file in a directory
write.xlsx(payment_schedule, file.path("data/", "Payment_Schedule.xlsx"))

# Also, export the main processed data with last payment info to another Excel file
write.xlsx(processed_data, file.path("data/","Processed_Data.xlsx"))
```

This flattens the list of payment dates and exports the results to Excel files.

## Conclusion

This document outlines the thought process and code explanation for the Payment Arrangements System Replication project. The project demonstrates the integration of data manipulation, date handling, and file exporting techniques to replicate the payment arrangements system. It highlights the ability to handle complex datasets and perform detailed calculations to produce meaningful outputs.
