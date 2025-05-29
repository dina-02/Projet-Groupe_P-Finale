import pandas as pd
import os
from constants import config_file, output_path, database_path
from repository import Repository
from sqlalchemy import create_engine
from helpers import get_serialized_data

class Model:
    """
    The Model class handles financial calculations and metrics for both countries and firms,
    using data loaded from the Repository.
    """

    def __init__(self, config, repo):
        """
        Initializes the Model with configuration and data repository.

        :param config: Configuration dictionary.
        :param repo: Repository object containing loaded data.
        """
        self.config = config
        self.repo = repo
        self.min = None
        self.max = None
        self.median = None
        self.average = None
        self.std = None
        self.quantile = None
        self.mean = None

        self.load_columns()
        self.load_new_columns()

    def load_columns(self): #voir comment raccourcir
        """
        Loads and stores column names for merged and raw datasets from the configuration.
        :return: none
        """

        self.col_merged = self.config['rename_merged_table']

        self.col_gdp_merged = self.col_merged['GDP (USD Trillions)']
        self.col_tax_rate_merged = self.col_merged['Corporate Tax Rate (%)']
        self.col_country_merged = self.col_merged['Headquarters']
        self.col_inflation = self.col_merged['Inflation Rate (%)']
        self.col_interest = self.col_merged['Interest Rate (%)']
        self.col_mean_revenue_merged = self.col_merged['Mean Revenue in (USD Million)']
        self.col_net_income_merged = self.col_merged['Mean Net Income in (USD Millions)']
        self.col_total_asset_merged = self.col_merged['Mean Total Asset in (USD Millions)']

        self.col = self.config['columns']['largest_companies']

        self.col_revenue = self.col['Revenue in (USD Million)']
        self.col_net_income = self.col['Net Income in (USD Millions)']
        self.col_industry = self.col['Industry']
        self.col_total_asset = self.col['Total Assest in (USD Millions)']
        self.col_company = self.col['Company']
        self.col_country = self.col['Headquarters']

    def load_new_columns(self): #voir comment raccourcir
        """
        Loads new calculated metric column names from the configuration.
        :return: none
        """


        self.countries_financial_summary_table = self.config['countries_financial_summary_table']

        self.revenue_to_gdp = self.countries_financial_summary_table['revenue_to_gdp']
        self.real_interest_rate = self.countries_financial_summary_table['real_interest_rate']
        self.average_contrib_to_pub_fin = self.countries_financial_summary_table['average_contrib_to_pub_fin']
        self.average_roa = self.countries_financial_summary_table['average_roa']

        self.firms_financial_summary_table = self.config['firms_financial_summary_table']

        self.asset_efficiency = self.firms_financial_summary_table['asset_efficiency']
        self.return_on_assets = self.firms_financial_summary_table['return_on_assets']

    def compute(self): #a voir
        """
        Computes basic statistics (mean, median, min, max, std, quantiles)
        for the GDP column in the merged dataset.
        :return: none
        """

        df = self.repo.merged_data.copy()

        col_gdp = df[self.col_gdp_merged]

        self.mean = col_gdp.mean()
        self.median = col_gdp.median()
        self.min = col_gdp.min()
        self.max = col_gdp.max()
        self.std = col_gdp.std()
        self.quantile = col_gdp.quantile([0.25, 0.5, 0.75])

    def get_revenue_to_gdp(self):
        """
        Calculates revenue as a percentage of GDP per country.
        :return: DataFrame with countries and their revenue-to-GDP ratios.
        """

        df = self.repo.merged_data.copy()

        df[self.revenue_to_gdp] = df[self.col_mean_revenue_merged]/(df[self.col_gdp_merged] * 1000000) * 100

        return df[[self.col_country_merged, self.revenue_to_gdp]]

    def get_real_interest_rate(self):
        """
        Computes the real interest rate (interest rate - inflation rate) per country.
        :return: DataFrame with countries and their real interest rates.
        """

        df = self.repo.merged_data.copy()

        df[self.real_interest_rate] = df[self.col_inflation] - df[self.col_interest]

        return df[[self.col_country_merged, self.real_interest_rate]]

    def get_asset_efficiency(self):
        """
        Calculates asset efficiency as revenue divided by total assets per firm.
        :return: DataFrame with companies and their asset efficiency.
        """

        df = self.repo.largest_companies.copy()

        df[self.asset_efficiency] = df[self.col_revenue] / df[self.col_total_asset]

        return df[[self.col_company, self.asset_efficiency]]

    def get_average_contribution_to_public_finances(self):
        """
        Estimates each country's average contribution to public finances based on tax rate and revenue.
        :return: DataFrame with countries and estimated contribution values.
        """

        df = self.repo.merged_data.copy()

        df[self.average_contrib_to_pub_fin] = ((df[self.col_tax_rate_merged] / 100) * df[
                                                  self.col_mean_revenue_merged]
                                                      / (df[self.col_gdp_merged] * 1_000_000)
                                              ) * 100

        return df[[self.col_country_merged,self.average_contrib_to_pub_fin]]

    def get_return_on_assets(self):
        """
        Calculates Return on Assets (ROA) for each firm.
        :return: DataFrame with companies and their ROA.
        """

        df = self.repo.largest_companies.copy()

        df[self.return_on_assets]=(df[self.col_net_income] / df[self.col_total_asset]) * 100

        return df[[self.col_company, self.return_on_assets]]

    def get_average_ROA_per_country(self):
        """
        Calculates average ROA per country based on aggregated company data.
        :return: DataFrame with countries and their average ROA.
        """

        df = self.repo.merged_data.copy()

        df[self.average_roa]=(df[self.col_net_income_merged] / df[self.col_total_asset_merged]) * 100

        q1 = df[self.average_roa].quantile(0.05)
        q2 = df[self.average_roa].quantile(0.95)
        df = df[(df[self.average_roa] >= q1) & (df[self.average_roa] <= q2)]

        return df[[self.col_country_merged, self.average_roa]]


    def get_roa_vs_efficiency(self):
        df = self.repo.largest_companies.copy()
        df['Return on Assets'] = (df[self.col_net_income] / df[self.col_total_asset]) * 100
        df['Asset Efficiency'] = df[self.col_revenue] / df[self.col_total_asset]
        return df[[self.col_company, 'Return on Assets', 'Asset Efficiency']]

    def get_top10_roa(self):
        df = self.get_return_on_assets()
        df = df.sort_values(by=self.return_on_assets, ascending=False).head(10)
        return df

    def get_contribution_vs_roa(self):
        df_roa = self.get_average_ROA_per_country()
        df_contrib = self.get_average_contribution_to_public_finances()

        df = pd.merge(df_roa, df_contrib, on=self.col_country_merged)
        return df

    def get_country_financial_summary(self):

        df2 = self.get_revenue_to_gdp()
        df3 = self.get_real_interest_rate()
        df4 = self.get_average_contribution_to_public_finances()
        df5 = self.get_average_ROA_per_country()

        df = df2.merge(df3, on=self.col_country_merged)
        df = df.merge(df4, on=self.col_country_merged)
        df = df.merge(df5, on=self.col_country_merged)

        print(df.head())

        return df

    def get_firms_financial_summary(self):

        df = self.get_asset_efficiency()
        df2 = self.get_return_on_assets()

        df = df2.merge(df, on=self.col_company)

        print(df.head())

        return df

    #NO USAGE
    def get_macro_correlation_matrix(self):
        df = self.get_country_financial_summary()
        df = df.set_index(self.col_country_merged)
        return df.corr()

    def export_datasets(self):
        country_financial_summary=self.get_country_financial_summary()
        firms_financial_summary=self.get_firms_financial_summary()

        engine = create_engine(f'sqlite:///{database_path}', echo=True)

        country_financial_summary.to_sql(self.config['export_final_results']['financial_summary_stat'],
                  con=engine, if_exists='replace', index=False)
        firms_financial_summary.to_sql(self.config['export_final_results']['firms_summary_stat'],
                  con=engine, if_exists='replace', index=False)


if __name__ == '__main__':
    config = get_serialized_data(os.path.join(os.getcwd(), config_file))
    repo = Repository(config=config, output_path=output_path)
    repo.get_data()

    model = Model(config=config, repo=repo)
    model.export_datasets()





