

# seting up the working directory to the folder of the GitHub repository.
setwd("/Users/AKB_CIM/Programming/R/Company's_projects/Intrum/Payment-Arrangements-System-Replication")

# Load necessary libraries
library(readr)       # For reading CSV files
library(dplyr)       # For data manipulation
library(lubridate)   # For date manipulation
library(tidyr)       # For unnesting data
library(openxlsx)    # For writing Excel files


# Read the CSV file
data <- read_csv("data/CaseStudy Data.csv", show_col_types = FALSE)

# View the first few rows of the data to understand its structure
head(data)
View(data)

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





# Process the data to calculate payment dates, last payment date, and last payment amount
processed_data <- data %>%
  rowwise() %>% # Process each row individually
  mutate(
    PaymentDates = list(calculate_payment_dates(ymd(FirstPaymentDate), Frequency, FrequencyType, FrequencyNumber, NumberOfPayments)), # Calculate payment dates
    LastPaymentDate = ifelse(length(PaymentDates) > 0, max(PaymentDates), NA), # Calculate last payment date
    LastPaymentAmount = ifelse(length(PaymentDates) > 0, TotalToPay - InstalmentAmount * (NumberOfPayments - 1), NA) # Calculate last payment amount
  ) %>%
  ungroup() # Ungroup to revert back to the original data structure


# View the processed data structure to ensure PaymentDates column is created correctly
str(processed_data)



# Convert all PaymentDates elements to Date type for consistency
processed_data <- processed_data %>%
  mutate(PaymentDates = lapply(PaymentDates, as.Date, origin = "1970-01-01"))

# Ensure PaymentDates column is properly created and all elements are of Date type
str(processed_data)
View(processed_data)




# Unnest the payment dates to create a flat structure
payment_schedule <- processed_data %>%
  unnest(PaymentDates) %>%
  select(CustomerReference, PaymentDates, InstalmentAmount)


# Rename columns for clarity in the final output
payment_schedule <- payment_schedule %>%
  rename(
    PaymentDate = PaymentDates,
    PaymentAmount = InstalmentAmount
  )

# View the payment schedule to verify the final output
head(payment_schedule)
View(payment_schedule)


# Export the payment schedule to an Excel file in a directory
library(openxlsx)
write.xlsx(payment_schedule, file.path("data/", "Payment_Schedule.xlsx"))


# Also, export the main processed data with last payment info to another Excel file
write.xlsx(processed_data, file.path("data/","Processed_Data.xlsx"))
