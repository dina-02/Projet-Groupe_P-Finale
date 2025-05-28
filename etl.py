import os
import pandas as pd

from constants import config_file
from helpers import get_serialized_data
from constants import financial_indicators_path, largest_companies_path
from helpers_export import dataframes_to_db

def get_config():
    """
    Load and return the project configuration dictionnary from the serialized config file path.
   :return: the serialized data
   """
   
    config_full_path = os.path.join(os.getcwd(), config_file)
    return get_serialized_data(config_full_path)

class Etl:
    """
    A class representing the ETL pipeline for processing financial indicators
    and company data into a merged, clean and analyzable format.
    """

    def __init__(self, config: dict, input_dir, sqlite_path):
        """
        Initialize the ETL process with configuration, input folder, and SQLite path.

        :param config: dict containing config parameters
        :param input_dir: folder path to input data
        :param sqlite_path: path where SQLite database will be written
        """

        self.config = config
        self.input_dir = input_dir
        self.sqlite_path = sqlite_path

        self.df_financial_indicators_raw = pd.DataFrame()
        self.df_financial_indicators = pd.DataFrame()
        self.df_largest_companies_aggregated = pd.DataFrame()
        self.df_largest_companies_raw = pd.DataFrame()
        self.df_largest_companies = pd.DataFrame()
        self.df_merged = pd.DataFrame()

    def extract(self):
        """
        Extract raw data from CSV sources intro pandas DataFrames.
        :return: none
        """

        self.df_financial_indicators_raw = pd.read_csv(financial_indicators_path, sep = ',')
        self.df_largest_companies_raw = pd.read_csv(largest_companies_path, sep = ',')

    def transform(self):
        """
        Apply a series of transformation steps: cleaning, aggregation, merging,
        and sorting the dataset by total assets.
        :return: none
        """

        self.clean_data()
        self.aggregate_data()
        self.merge_data()
        self.sort_countries_by_total_assets()

    def clean_data(self):
        """
        Clean the raw datasets by replacing 0s with NaN, dropping empty and duplicate rows,
        and renaming columns based on configuration mappings.
        :return: none
        """

        self.df_financial_indicators = self.df_financial_indicators_raw.copy()
        self.df_largest_companies = self.df_largest_companies_raw.copy()

        for df in [self.df_financial_indicators, self.df_largest_companies]:
            df.replace(0, pd.NA, inplace=True)
            df.dropna(how='all', inplace=True)
            df.drop_duplicates(inplace=True)

        self.df_largest_companies.rename(columns=self.config['columns']['largest_companies'], inplace=True)

    def aggregate_data(self):
        """
        Group the company data by country, compute the mean of numeric values,
        and rename the columns for aggregated output.
        :return: none
        """

        self.df_largest_companies.rename(self.config['columns']['largest_companies'], inplace=True)

        df = self.df_largest_companies.copy()

        df.drop(self.config['drop_columns_largest_companies'], axis = 1, inplace = True)


        df_mean = (df.groupby('Country', as_index = False)
                                                .mean(numeric_only =True))

        df_mean.rename(columns = self.config['columns']['largest_companies_aggregated'], inplace = True)

        self.df_largest_companies_aggregated = df_mean

    def merge_data(self):
        """
        Merge aggregated company data with financial indicators on the 'Country' column.
        Column names are renamed according to config after merging.
        :return: none
        """

        self.df_merged = pd.merge(
            self.df_largest_companies_aggregated,
            self.df_financial_indicators,
            how = 'left',
            on = 'Country'
        )

        self.df_merged.rename(columns=self.config['rename_merged_table'], inplace = True)

    def sort_countries_by_total_assets(self):
        """
        Sort the merged dataset in descending order based on mean total assets.
        :return: the sorted dataframe by mean total assets
        """

        self.df_merged.sort_values(
            by = 'Mean_Total_Asset',
            ascending = False,
            inplace = True
        )
        return self.df_merged

    def load(self) -> None:
        """
        Export the transformed datasets to both SQLite (if enabled)
        and CSV (if enabled), based on configuration.
        :return: none
        """

        export_sql = {
            self.config['files_sql']['merged_table']: self.df_merged,
            self.config['files_sql']['source_largest_companies']: self.df_largest_companies
        }

        export_csv = {
            self.config['files_csv']['merged_table']: self.df_merged,
            self.config['files_csv']['source_largest_companies']: self.df_largest_companies
        }

        if self.config['etl_main_parameters']['to_sqlite']:
            dataframes_to_db(
                export_sql,
                db_path=self.sqlite_path,
                drop_all_tables=self.config['etl_main_parameters']['drop_all_tables'],
            )

        if self.config['etl_main_parameters']['to_csv']:
            output_folder = self.config['folders']['output_folder']
            os.makedirs(output_folder, exist_ok = True)

            for name, df in export_csv.items():
                csv_path = os.path.join(output_folder, f'{name}')
                df.to_csv(csv_path, index = False)

if __name__ == '__main__':
    config = get_config()
    etl = Etl(config = config, input_dir = 'input', sqlite_path = 'output/output.sqlite')
    etl.extract()
    etl.transform()
    etl.load()
