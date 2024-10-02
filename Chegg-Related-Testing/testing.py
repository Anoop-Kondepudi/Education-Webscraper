# List of months with 31 days
months_31 = ["january", "march", "may", "july", "august", "october", "december"]
# List of months with 30 days
months_30 = ["april", "june", "september", "november"]
# List of months with 28/29 days
february = "february"

# Start and end year
start_year = 2006
end_year = 2024

# Special end month and day for 2024
end_month = "august"
end_day = 31

# Output file name
output_file = "chegg_all_urls.txt"

def generate_all_urls(start_year, end_year, end_month, end_day, output_file):
    with open(output_file, 'w') as file:
        for year in range(start_year, end_year + 1):
            for month in months_31 + months_30 + [february]:
                # Determine the number of days in the month
                if month == february:
                    # Check for leap year
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        days_in_month = 29
                    else:
                        days_in_month = 28
                elif month in months_31:
                    days_in_month = 31
                else:
                    days_in_month = 30
                
                # For the end year, adjust the month and day
                if year == end_year:
                    # If the month is after the end month, skip
                    if month > end_month:
                        continue
                    # If the month is the end month, use the end day
                    if month == end_month:
                        days_in_month = end_day
                
                # Generate URLs for each day in the month
                for day in range(1, days_in_month + 1):
                    url = f"https://www.chegg.com/homework-help/questions-and-answers/physics-archive-{year}-{month}-{str(day).zfill(2)}"
                    file.write(url + "\n")

generate_all_urls(start_year, end_year, end_month, end_day, output_file)

print(f"All URLs have been generated and saved to {output_file}")
