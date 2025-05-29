"""
This module defines global file paths used throughout the project.

These constants are used to access configuration files, input datasets,
and output directories in a consistent and centralized way.

Constants:
    config_file (str): Path to the main YAML configuration file.
    output_path (str): Directory path where processed files will be saved.
    database_path (str): Path to the SQLite database file.
    financial_indicators_path (str): CSV file containing macroeconomic indicators per country.
    largest_companies_path (str): CSV file containing information about the largest global companies.
"""

# Path to the YAML configuration file for the ETL and visualization settings
config_file = r'input/config.yaml'

#Path to the input files
input_dir = r'input'

# Directory where output CSVs and files will be stored
output_path = r'output'

# SQLite database file path to store structured datasets
database_path = r'output/output.sqlite'

# Input CSV file containing country-level financial indicators (e.g., GDP, inflation)
financial_indicators_path = r'input/financial_indicators.csv'

# Input CSV file containing firm-level data for the largest global companies
largest_companies_path = r'input/largest_companies.csv'

