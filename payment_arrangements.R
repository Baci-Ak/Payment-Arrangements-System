

# Load necessary libraries
library(readr)       # For reading CSV files
library(dplyr)       # For data manipulation
library(lubridate)   # For date manipulation
library(tidyr)       # For unnesting data
library(openxlsx)    # For writing Excel files

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

# Function to process data and calculate payment dates
process_payment_data <- function(input_path, output_dir) {
  # Read the CSV file
  data <- read_csv(input_path, show_col_types = FALSE)
  
  # Process the data to calculate payment dates, last payment date, and last payment amount
  processed_data <- data %>%
    rowwise() %>% # Process each row individually
    mutate(
      PaymentDates = list(calculate_payment_dates(ymd(FirstPaymentDate), Frequency, FrequencyType, FrequencyNumber, NumberOfPayments)), # Calculate payment dates
      LastPaymentDate = ifelse(length(PaymentDates) > 0, max(PaymentDates), NA), # Calculate last payment date
      LastPaymentAmount = ifelse(length(PaymentDates) > 0, TotalToPay - InstalmentAmount * (NumberOfPayments - 1), NA) # Calculate last payment amount
    ) %>%
    ungroup() # Ungroup to revert back to the original data structure
  
  # Convert all PaymentDates elements to Date type for consistency
  processed_data <- processed_data %>%
    mutate(PaymentDates = lapply(PaymentDates, as.Date, origin = "1970-01-01"))
  
  # Unnest the payment dates to create a flat structure
  payment_schedule <- processed_data %>%
    unnest(PaymentDates) %>%
    select(CustomerReference, PaymentDates, InstalmentAmount) %>%
    rename(
      PaymentDate = PaymentDates,
      PaymentAmount = InstalmentAmount
    )
  
  # Export the payment schedule to an Excel file in a directory
  write.xlsx(payment_schedule, file.path(output_dir, "Payment_Schedule.xlsx"))
  
  # Also, export the main processed data with last payment info to another Excel file
  write.xlsx(processed_data, file.path(output_dir, "Processed_Data.xlsx"))
}

# Command-line arguments for input path and output directory
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 2) {
  input_path <- args[1]
  output_dir <- args[2]
  process_payment_data(input_path, output_dir)
} else {
  stop("Please provide input CSV file path and output directory path as arguments.")
}
