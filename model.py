import pandas as pd

from helpers import compute_ratio
from sqlalchemy import create_engine

class Model:
    """
    The Model class handles financial calculations and metrics generation for both countries and firms,
    using data loaded from the Repository.
    """

    def __init__(self, config, repo):
        """
        Initializes the Model with configuration and data repository.

        :param config: Configuration dictionary with column mappings and settings.
        :param repo: Repository object that provides access to cleaned and loaded data.
        """

        self.config = config
        self.repo = repo

        #load old columns
        self.col_merged = self.config['merged_dataset']['columns']
        self.col = self.config['largest_companies']['columns']

        #load new columns
        self.countries_financial_summary_table = self.config['countries_financial_summary_table']
        self.firms_financial_summary_table = self.config['firms_financial_summary_table']


    def get_revenue_to_gdp(self) -> pd.DataFrame:
        """
        Calculates the mean revenue as a percentage of GDP for each country.
        :return: DataFrame with country names and their revenue-to-GDP ratio.
        """

        df = self.repo.merged_data.copy()

        # GDP is in trillions -> convert to millions before dividing
        df[self.countries_financial_summary_table['revenue_to_gdp']] =  (df[self.col_merged['mean_revenue']]
                                                                         / (df[self.col_merged['gdp_usd_trillions']]
                                                                            * 1000000) * 100)

        return df[[self.col_merged['country'], self.countries_financial_summary_table['revenue_to_gdp']]]


    def get_real_interest_rate(self) -> pd.DataFrame:
        """
        Computes the real interest rate by subtracting inflation from the nominal interest rate.
        :return: DataFrame with country names and their real interest rates.
        """

        df = self.repo.merged_data.copy()

        df[self.countries_financial_summary_table['real_interest_rate']] = (df[self.col_merged['interest_rate']]
                                                                            - df[self.col_merged['inflation_rate']])

        return df[[self.col_merged['country'], self.countries_financial_summary_table['real_interest_rate']]]


    def get_average_contribution_to_public_finances(self) -> pd.DataFrame:
        """
        Estimates each country's average contribution to public finances based on revenue and tax rate.
        :return: DataFrame with countries and their estimated fiscal contribution percentages.
        """

        df = self.repo.merged_data.copy()

        # Estimate public contribution: (tax rate * revenue) / GDP
        df[self.countries_financial_summary_table['average_contrib_to_pub_fin']] = (
                                                (df[self.col_merged['corporate_tax_rate']] / 100) *
                                                df[self.col_merged['mean_revenue']]
                                                      / (df[self.col_merged['gdp_usd_trillions']] * 1000000)) * 100

        return df[[self.col_merged['country'], self.countries_financial_summary_table['average_contrib_to_pub_fin']]]


    def get_average_roa_per_country(self) -> pd.DataFrame:
        """
        Computes the average Return on Assets (ROA) per country.

        This function filters out extreme values (5th and 95th percentiles) for better reliability.
        :return: DataFrame with country names and their average ROA values.
        """

        df = self.repo.merged_data.copy()

        # ROA = Net Income / Total Assets
        df=compute_ratio(df=df, num=self.col_merged['mean_net_income'], denom=self.col_merged['mean_total_asset'],
                         result=self.countries_financial_summary_table['average_roa'], x=100)

        # Filter extreme outliers using 5th and 95th percentiles
        q1 = df[self.countries_financial_summary_table['average_roa']].quantile(0.05)
        q2 = df[self.countries_financial_summary_table['average_roa']].quantile(0.95)
        df = df[(df[self.countries_financial_summary_table['average_roa']] >= q1) & (
                df[self.countries_financial_summary_table['average_roa']] <= q2)]

        return df[[self.col_merged['country'], self.countries_financial_summary_table['average_roa']]]


    def get_firms_financial_summary(self) -> pd.DataFrame:
        """
        Computes financial efficiency metrics for individual companies.

        Includes Return on Assets and Revenue-to-Asset ratios.
        :return: DataFrame with companies, ROA, and asset efficiency.
        """

        df = self.repo.largest_companies.copy()

        # Efficiency = Revenue / Assets
        df = compute_ratio(df=df, num=self.col['revenue_usd_millions'], denom=self.col['total_asset_usd_millions'],
                                       result=self.firms_financial_summary_table['asset_efficiency'])

        # ROA = Net Income / Assets
        df = compute_ratio(df=df, num=self.col['net_income_usd_millions'], denom=self.col['total_asset_usd_millions'],
                          result=self.firms_financial_summary_table['return_on_assets'], x=100)

        df = df[[self.col['company'], self.firms_financial_summary_table['asset_efficiency'],
                 self.firms_financial_summary_table['return_on_assets']]].round(3)

        return  df


    def get_country_financial_summary(self) -> pd.DataFrame:
        """
        Aggregates all country-level metrics into a single DataFrame.

        Merges revenue-to-GDP, real interest rate, public finance contribution, and ROA.
        :return: Final country-level DataFrame containing financial summaries.
        """

        df2 = self.get_revenue_to_gdp()
        df3 = self.get_real_interest_rate()
        df4 = self.get_average_contribution_to_public_finances()
        df5 = self.get_average_roa_per_country()

        # Merge datasets step-by-step on the country column
        df = df2.merge(df3, on=self.col_merged['country'])
        df = df.merge(df4, on=self.col_merged['country'])
        df = df.merge(df5, on=self.col_merged['country'])

        df = df.round(3)

        return df


    def export_datasets_to_sqlite(self, database_path: str) -> None:
        """
        Exports the summarized country and firm financial datasets to a SQLite database.

        The data is saved under table names specified in the configuration file.
        """

        try:
            country_financial_summary = self.get_country_financial_summary()
            firms_financial_summary = self.get_firms_financial_summary()

            engine = create_engine(f'sqlite:///{database_path}', echo=True)

            # Save both summaries to named tables defined in the config
            country_financial_summary.to_sql(self.config['export_final_results']['financial_summary_stat'],
                      con=engine, if_exists='replace', index=False)
            firms_financial_summary.to_sql(self.config['export_final_results']['firms_summary_stat'],
                      con=engine, if_exists='replace', index=False)
        except Exception as e:
            print(f'Error during the export, {e}')

