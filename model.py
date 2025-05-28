import pandas as pd
from constants import config_file, output_path, database_path
from repository import Repository

class Model:
    def __init__(self, config, repo):
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

    def load_columns(self):

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

    def load_new_columns(self):
        self.countries_financial_summary_table = self.config['countries_financial_summary_table']

        self.revenue_to_gdp = self.countries_financial_summary_table['revenue_to_gdp']
        self.real_interest_rate = self.countries_financial_summary_table['real_interest_rate']
        self.average_contrib_to_pub_fin = self.countries_financial_summary_table['average_contrib_to_pub_fin']
        self.average_roa = self.countries_financial_summary_table['average_roa']

        self.firms_financial_summary_table = self.config['firms_financial_summary_table']

        self.asset_efficiency = self.firms_financial_summary_table['asset_efficiency']
        self.return_on_assets = self.firms_financial_summary_table['return_on_assets']

    def compute(self):
        df = self.repo.merged_data.copy()

        col_gdp = df[self.col_gdp_merged]

        self.mean = col_gdp.mean()
        self.median = col_gdp.median()
        self.min = col_gdp.min()
        self.max = col_gdp.max()
        self.std = col_gdp.std()
        self.quantile = col_gdp.quantile([0.25, 0.5, 0.75])

    # def get_biggest_sector(self):
    #     df = self.repo.largest_companies.copy()
    #
    #     df[self.revenue_to_gdp] = df[self.col_net_income] / df[self.col_revenue] * 100
    #     biggest_sector = df.groupby(self.col_industry, as_index=False)[self.revenue_to_gdp].mean().sort_values(by = 'Profit Margin (%)', ascending = False)
    #
    #     print(biggest_sector.head())
    #     return biggest_sector

    def get_revenue_to_gdp(self):
        df = self.repo.merged_data.copy()

        df[self.revenue_to_gdp] = df[self.col_mean_revenue_merged]/(df[self.col_gdp_merged] * 1000000) * 100

        return df[[self.col_country_merged, self.revenue_to_gdp]]

    def get_real_interest_rate(self):
        df = self.repo.merged_data.copy()

        df[self.real_interest_rate] = df[self.col_inflation] - df[self.col_interest]

        return df[[self.col_country_merged, self.real_interest_rate]]

    def get_asset_efficiency(self):
        df = self.repo.largest_companies.copy()

        df[self.asset_efficiency] = df[self.col_revenue] / df[self.col_total_asset]

        return df[[self.col_company, self.asset_efficiency]]

    def get_average_contribution_to_public_finances(self):
        df = self.repo.merged_data.copy()
        ### *100000 je pense
        df[self.average_contrib_to_pub_fin] = ((df[self.col_tax_rate_merged] * df[self.col_mean_revenue_merged]) / df[
                                                self.col_gdp_merged]) * 100

        return df[[self.col_country_merged,self.average_contrib_to_pub_fin]]

    def get_return_on_assets(self):
        df = self.repo.largest_companies.copy()

        df[self.return_on_assets] = (df[self.col_net_income] / df[self.col_total_asset]) * 100

        return df[[self.col_company, self.return_on_assets]]

    def get_average_ROA_per_country(self):
        df = self.repo.merged_data.copy()

        df[self.average_roa] = (df[self.col_net_income_merged] / df[self.col_total_asset_merged]) * 100

        return df[[self.col_country_merged, self.average_roa]]

    def get_inflation_vs_interest(self):
        df = self.repo.merged_data.copy()
        return df[[self.col_inflation, self.col_interest, self.col_country_merged]]

    def get_roa_vs_efficiency(self):
        df = self.repo.largest_companies.copy()
        df['Return on Assets'] = (df[self.col_net_income] / df[self.col_total_asset]) * 100
        df['Asset Efficiency'] = df[self.col_revenue] / df[self.col_total_asset]
        return df[[self.col_company, 'Return on Assets', 'Asset Efficiency']]

    def get_top10_roa(self):
        df = self.get_return_on_assets()
        df = df.sort_values(by=self.return_on_assets, ascending=False).head(10)
        return df

    def get_country_financial_summary(self):

        df2 = self.get_revenue_to_gdp()
        df3 = self.get_real_interest_rate()
        df4 = self.get_average_contribution_to_public_finances()
        df5 = self.get_average_ROA_per_country()

        df = df2.merge(df3, on = self.col_country_merged)
        df = df.merge(df4, on = self.col_country_merged)
        df = df.merge(df5, on = self.col_country_merged)

        return df

    def get_firms_financial_summary(self):

        df = self.get_asset_efficiency()
        df2 = self.get_return_on_assets()

        df = df2.merge(df, on=self.col_company)

        return df


if __name__ == '__main__':
    from constants import config_file
    from helpers import get_serialized_data
    import os

    config = get_serialized_data(os.path.join(os.getcwd(), config_file))
    repo = Repository(config=config, output_path = output_path, database_path=database_path)
    repo.get_data()

    model = Model(config = config, repo = repo)
    #model.get_biggest_sector()





