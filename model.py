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

    def compute(self):
        df = self.repo.merged_data.copy()

        col_gdp = df[self.col_gdp_merged]

        self.mean = col_gdp.mean()
        self.median = col_gdp.median()
        self.min = col_gdp.min()
        self.max = col_gdp.max()
        self.std = col_gdp.std()
        self.quantile = col_gdp.quantile([0.25, 0.5, 0.75])

    #changer pour ne pas utiliser les noms directement

#je pense que c'est a enlever
    def get_biggest_sector(self):
        df = self.repo.largest_companies.copy()

        df['Profit Margin (%)'] = df[self.col_net_income] / df[self.col_revenue] * 100
        biggest_sector = df.groupby(self.col_industry, as_index=False)['Profit Margin (%)'].mean().sort_values(by = 'Profit Margin (%)', ascending = False)

        print(biggest_sector.head())
        return biggest_sector

    def get_revenue_to_gdp(self):
        df = self.repo.merged_data.copy()

        df['Revenue to GDP (%)'] = df[self.col_mean_revenue_merged]/(df[self.col_gdp_merged] * 1000000) * 100

        return df[[self.col_country_merged, 'Revenue to GDP (%)']]

    def get_real_interest_rate(self):
        df = self.repo.merged_data.copy()

        df['Real Interest Rate (%)'] = df[self.col_inflation] - df[self.col_interest]

        return df[[self.col_country_merged, 'Real Interest Rate (%)']]

    def get_asset_efficiency(self):
        df = self.repo.largest_companies.copy()

        df['Asset Efficiency'] = df[self.col_revenue] / df[self.col_total_asset]

        return df[[self.col_company, 'Asset Efficiency']]

    def get_average_contribution_to_public_finances(self):
        df = self.repo.merged_data.copy()
        ### *100000 je pense
        df['Average Contribution to Public Finances (% of GDP)'] = ((df[self.col_tax_rate_merged] * df[self.col_mean_revenue_merged]) / df[
                                                self.col_gdp_merged]) * 100

        return df[[self.col_country_merged, 'Average Contribution to Public Finances (% of GDP)']]

    def get_return_on_assets(self):
        df = self.repo.largest_companies.copy()

        df['Return on Assets'] = (df[self.col_net_income] / df[self.col_total_asset]) * 100

        return df[[self.col_company, 'Return on Assets']]

    def get_average_ROA_per_country(self):
        df = self.repo.merged_data.copy()

        df['Average ROA'] = (df[self.col_net_income_merged] / df[self.col_total_asset_merged]) * 100

        return df[[self.col_country_merged, 'Average ROA']]

    def get_inflation_vs_interest(self):
        df = self.repo.merged_data.copy()
        return df[[self.col_inflation, self.col_interest, self.col_country_merged]]

    def get_new_table(self):  #changer le nom je manque d'inspi

        df2 = self.get_revenue_to_gdp()
        df3 = self.get_real_interest_rate()
        df4 = self.get_average_contribution_to_public_finances()
        df5 = self.get_average_ROA_per_country()

        df = df2.merge(df3, on = self.col_country_merged)
        df = df.merge(df4, on = self.col_country_merged)
        df = df.merge(df5, on = self.col_country_merged)

        return df

    def get_another_new_table(self): #changer nom

        df = self.get_asset_efficiency()
        df2 = self.get_return_on_assets()

        df = df2.merge(df, on=self.col_company)

        return df


if __name__ == '__main__':
    from constants import config_file
    from helpers import get_serialized_data
    import os

    config = get_serialized_data(os.path.join(os.getcwd(), config_file))
    repo = Repository(config=config, output_path = 'output')
    repo.get_data()

    model = Model(config = config, repo = repo)
    model.get_biggest_sector()





