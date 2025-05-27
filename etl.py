import os

import pandas as pd

from constants import config_file
from helpers import get_serialized_data
from constants import financial_indicators_path, largest_companies_path


def get_config():
    config_full_path = os.path.join(os.getcwd(), config_file)
    return get_serialized_data(config_full_path)

class Etl:
    def __init__(self, config: dict, input_dir, sqlite_path):
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
        ''''''
        self.df_financial_indicators_raw = pd.read_csv(financial_indicators_path, sep = ',')
        self.df_largest_companies_raw = pd.read_csv(largest_companies_path, sep = ',')

    def transform(self):
        self.clean_data()
        self.aggregate_data()
        self.merge_data()

    def clean_data(self):

        self.df_financial_indicators = self.df_financial_indicators_raw.copy()
        self.df_largest_companies = self.df_largest_companies_raw.copy()

        for df in [self.df_financial_indicators, self.df_largest_companies]:
            df.replace(0, pd.NA, inplace=True)
            df.dropna(how='all', inplace=True)
            df.drop_duplicates(inplace=True)

    def aggregate_data(self):

        df = self.df_largest_companies.copy()

        df_mean = (df.groupby('Headquarters', as_index = False)
                                                .mean(numeric_only =True)
                                                )

        renamed_columns = {
            col: f"Mean {col}" for col in df_mean.columns if col != "Headquarters"
        }
        df_mean.rename(columns = renamed_columns, inplace = True)

        df_mean.drop(columns = ['Mean Rank'], inplace=True)
        self.df_largest_companies_aggregated = df_mean


    def merge_data(self):

        self.df_merged = pd.merge(
            self.df_largest_companies_aggregated,
            self.df_financial_indicators,
            how="left",
            left_on="Headquarters",
            right_on="Country"
        )

        self.df_merged.drop(columns=['Country'], inplace = True)

    # def load(self) -> None:
    #
    #     export = {
    #         self.config['files']['merged_table']: self.df_merged,
    #         self.config['files']['source_largest_companies']: self.df_largest_companies
    #     }
    #
    #     print(self.sqlite_path)
    #     if self.config["etl_main_parameters"]["to_sqlite"]:
    #         dataframes_to_db(
    #             export,
    #             db_path=self.sqlite_path,
    #             drop_all_tables=self.config["etl_main_parameters"]["drop_all_tables"],
    #         )
    #         print(f"Export file to SQLite: {self.sqlite_path}")

    def load(self) -> None:
        export = {
            self.config['files']['merged_table']: self.df_merged,
            self.config['files']['source_largest_companies']: self.df_largest_companies
        }

        output_folder = self.config["folders"]["output_folder"]
        os.makedirs(output_folder, exist_ok=True)

        for name, df in export.items():
            csv_path = os.path.join(output_folder, f"{name}")
            df.to_csv(csv_path, index=False)
            print(f" Exporté vers CSV : {csv_path}")

    def sort_countries_by_total_assets(self):
        """
        merged_table trié en fonction des mean assets (à changer).
        """
        if self.df_merged.empty:
            raise ValueError("Le DataFrame df_merged est vide. Lancez extract() et transform() avant.")

        sorted_df = self.df_merged.sort_values(
            by="Mean Total Assest in (USD Millions)",  # garder la faute ici??? Prévenir Loane
            ascending=False
        )

        return sorted_df

if __name__ == "__main__":
    config = get_config()
    etl = Etl(config=config, input_dir="input", sqlite_path="output/output.sqlite")
    etl.extract()
    etl.transform()
    etl.load()

