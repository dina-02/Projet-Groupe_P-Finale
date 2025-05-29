import os
import pandas as pd

from constants import config_file, input_dir
from helpers import get_serialized_data
from constants import financial_indicators_path, largest_companies_path

def get_config() -> dict:
    """
    Load and return the project configuration dictionary from the serialized config file path.
   :return: the serialized data
   """

    # Build the full path to the config file and load the data
    config_full_path = os.path.join(os.getcwd(), config_file)
    return get_serialized_data(config_full_path)

class ETL:
    """
    A class representing the ETL pipeline for processing financial indicators
    and company data into a merged, clean and analyzable format.
    """

    def __init__(self, config: dict, input_dir: str) -> None:
        """
        Initialize the ETL process with configuration, input folder.

        :param config: dict containing config parameters
        :param input_dir: folder path to input data
        """

        self.config = config
        self.input_dir = input_dir

        # Initialize dataframes for each ETL stage
        self.df_financial_indicators_raw = pd.DataFrame()
        self.df_financial_indicators = pd.DataFrame()
        self.df_largest_companies_aggregated = pd.DataFrame()
        self.df_largest_companies_raw = pd.DataFrame()
        self.df_largest_companies = pd.DataFrame()
        self.df_merged = pd.DataFrame()

    def extract(self) -> None:
        """
        Extract raw data from CSV sources intro pandas DataFrames.
        :return: none
        """

        # Load the raw CSV files for financial indicators and company data
        try:
            self.df_financial_indicators_raw = pd.read_csv(financial_indicators_path, sep=',')
            self.df_largest_companies_raw = pd.read_csv(largest_companies_path, sep=',')
        except FileNotFoundError as e:
            print(f'[Error] File not found : {e}')


    def transform(self) -> None:
        """
        Apply a series of transformation steps: cleaning, aggregation, merging,
        and sorting the dataset by total assets.
        :return: none
        """

        self.clean_data()
        self.aggregate_data()
        self.merge_data()
        self.sort_countries_by_total_assets()

    def clean_data(self) -> None:
        """
        Clean the raw datasets by replacing 0s with NaN, dropping empty and duplicate rows,
        and renaming columns based on configuration mappings.
        :return: none
        """

        # Make copies of the original raw data
        self.df_financial_indicators = self.df_financial_indicators_raw.copy()
        self.df_largest_companies = self.df_largest_companies_raw.copy()

        # Apply cleaning to both datasets
        for df in [self.df_financial_indicators, self.df_largest_companies]:
            df.replace(0, pd.NA, inplace=True)
            df.dropna(how='all', inplace=True)
            df.drop_duplicates(inplace=True)

        # Rename columns in the company data using config mappings
        self.df_largest_companies.rename(columns=self.config['columns']['largest_companies'],
                                         inplace=True)

    def aggregate_data(self) -> None:
        """
        Group the company data by country, compute the mean of numeric values,
        and rename the columns for aggregated output.
        :return: none
        """

        self.df_largest_companies.rename(self.config['columns']['largest_companies'],
                                         inplace=True)

        df=self.df_largest_companies.copy()

        # Drop the columns not needed for aggregation
        df.drop(self.config['drop_columns_largest_companies'], axis=1, inplace=True)

        # Group by country and compute the mean for numeric columns
        df_mean=(df.groupby(self.config['columns']['largest_companies']['Headquarters'], as_index=False)
                                            .mean(numeric_only=True))
        # Rename the resulting aggregated columns
        df_mean.rename(columns=self.config['columns']['largest_companies_aggregated'],
                       inplace=True)

        self.df_largest_companies_aggregated = df_mean

    def merge_data(self) -> None:
        """
        Merge aggregated company data with financial indicators on the 'Country' column.
        Column names are renamed according to config after merging.
        :return: none
        """

        merge_col = self.config['columns']['largest_companies']['Headquarters']

        self.df_merged = pd.merge(
            self.df_largest_companies_aggregated,
            self.df_financial_indicators,
            how='left',
            on=merge_col)

        # Rename merged columns based on config
        self.df_merged.rename(columns=self.config['rename_merged_table'],
                              inplace=True)

        self.df_merged = self.df_merged.round(3)

    def sort_countries_by_total_assets(self) -> pd.DataFrame:
        """
        Sort the merged dataset in descending order based on mean total assets.
        :return: the sorted dataframe by mean total assets
        """

        mean_total_asset = self.config['rename_merged_table']['Mean Total Asset in (USD Millions)']

        self.df_merged.sort_values(
            by=mean_total_asset,
            ascending=False,
            inplace=True)

        self.df_merged[mean_total_asset] = self.df_merged[mean_total_asset].round(2)

        return self.df_merged

    def load(self) -> None:
        """
        Export the transformed datasets CSV.
        :return: none
        """

        export = {
            self.config['files_csv']['merged_table']: self.df_merged,
            self.config['files_csv']['source_largest_companies']: self.df_largest_companies
        }

        try:
            output_folder = self.config['folders']['output_folder']
            os.makedirs(output_folder, exist_ok = True)

            # Save each DataFrame to CSV in the output directory
            for name, df in export.items():
                csv_path = os.path.join(output_folder, f'{name}')
                df.to_csv(csv_path, index = False)
        except PermissionError as e:
            print(f'[Error] Datasets not exported: {e}')

    def run(self) -> None:
        self.extract()
        self.transform()
        self.load()

# Script entry point
if __name__ == '__main__':
    '''
    Executes the entire ETL: extract, transform, load.
    The data will be extracted, cleaned and exported to CSV.
    '''
    config = get_config()
    etl = ETL(config=config, input_dir=input_dir)
    etl.run()
