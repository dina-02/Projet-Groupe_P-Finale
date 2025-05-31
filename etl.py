import os
import pandas as pd

from constants import config_file, input_dir, financial_indicators_path, largest_companies_path
from helpers import get_serialized_data


def get_config() -> dict:
    """
    Load and return the project configuration dictionary from the serialized config file path.
    :return: the serialized data
    """

    # Build the full path to the config file and load the data
    config_full_path = os.path.join(os.getcwd(), config_file)
    return get_serialized_data(config_full_path)


class Etl:
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

        self.largest_comp_col = self.config['largest_companies']
        self.merged_dataset = self.config['merged_dataset']['columns']

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

        self.largest_comp_col = self.config['largest_companies']

        print(f'before the renaming: {self.df_largest_companies.columns}')
        print(f'before the renaming: {self.df_financial_indicators.columns}')


        # Apply cleaning to both datasets
        for df in [self.df_financial_indicators, self.df_largest_companies]:
            df.replace(0, pd.NA, inplace=True)
            df.dropna(how='all', inplace=True)
            df.drop_duplicates(inplace=True)
            df.columns=(df.columns
                        .str.replace(r' \(% of GDP\)', '', regex=True)
                        .str.replace(r' in \(USD Million\)', ' usd millions', regex=True)
                        .str.replace(r' in \(USD Millions\)', ' usd millions', regex=True)
                        .str.replace(r' \(%\)', ' ', regex=True)
                        .str.replace(r' \(USD Trillions\)', ' usd trillions', regex=True)
                        .str.strip()
                        .str.replace(' ', '_')
                        .str.lower())
            df.rename(columns={'total_assest_usd_millions':'total_asset_usd_millions'}, inplace=True)  # pour que ca soit correct dans yaml

        self.df_largest_companies.rename(columns=self.largest_comp_col['columns'], inplace=True)

        print(f'after the renaming: {self.df_largest_companies.columns}')
        print(f'after the renaming: {self.df_financial_indicators.columns}')

    def aggregate_data(self) -> None:
        """
        Group the company data by country, compute the mean of numeric values,
        and rename the columns for aggregated output.
        :return: none
        """

        df = self.df_largest_companies.copy()

        print(f'before aggregation: {df.columns}')

        # Drop the columns not needed for aggregation
        df.drop(self.largest_comp_col['drop_columns_largest_companies'], axis=1, inplace=True)

        # Group by country and compute the mean for numeric columns
        df_mean=(df.groupby(self.largest_comp_col['columns']['headquarters'], as_index=False)
                                            .mean(numeric_only=True))

        print(f'before the renaming of df_mean: {df_mean.columns}')

        # Rename the resulting aggregated columns
        df_mean.rename(columns=self.largest_comp_col['aggregated'],
                       inplace=True)

        print(f'after the renaming of df_mean: {df_mean.columns}')

        self.df_largest_companies_aggregated = df_mean

        print(f'after aggregation: {self.df_largest_companies_aggregated.columns}')

    def merge_data(self) -> None:
        """
        Merge aggregated company data with financial indicators on the 'Country' column.
        Column names are renamed according to config after merging.
        :return: none
        """

        merge_col = self.config['merged_dataset']['merge_on']

        self.df_merged = pd.merge(
            self.df_largest_companies_aggregated,
            self.df_financial_indicators,
            how='inner',
            on=merge_col)

        print(f'new names merged table: {self.df_merged.columns}')

        # Rename merged columns based on config
        self.df_merged.rename(columns=self.config['merged_dataset']['columns'],
                              inplace=True)

        self.df_merged = self.df_merged.round(3)


    def sort_countries_by_total_assets(self) -> pd.DataFrame:
        """
        Sort the merged dataset in descending order based on mean total assets.
        :return: the sorted dataframe by mean total assets
        """

        mean_total_asset = self.merged_dataset['mean_total_asset']

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
            self.config['output_files_csv']['merged_table']: self.df_merged,
            self.config['output_files_csv']['largest_companies']: self.df_largest_companies
        }

        try:
            output_folder = self.config['folders']['output_folder']
            os.makedirs(output_folder, exist_ok=True)

            # Save each DataFrame to CSV in the output directory
            for name, df in export.items():
                csv_path = os.path.join(output_folder, f'{name}')
                df.to_csv(csv_path, index=False)
        except PermissionError as e:
            print(f'[Error] Datasets not exported: {e}')


    def sanity_check(self):
        print("**** sanity check ****")
        print(f"df_merged={self.df_merged.shape}")
        print(f"df_largest_companies={self.df_largest_companies.shape}")
        print(f"df_merged={self.df_merged.describe()}")
        print(f"df_largest_companies={self.df_largest_companies.describe()}")


    def run(self) -> None:
        self.extract()
        self.transform()
        self.load()


# Script entry point
if __name__ == '__main__':
    '''
    Executes the entire ETL and the sanity check.
    The data will be extracted, cleaned and exported to CSV.
    '''
    config = get_config()
    etl = Etl(config=config, input_dir=input_dir)
    etl.run()
    etl.sanity_check()
