import pandas as pd
from constants import config_file
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

        self.col_gdp_merged = self.config['rename_merged_table']['GDP (USD Trillions)']
        self.col_revenue_merged = self.config['rename_merged_table']['Mean Net Income in (USD Millions)']
        self.col_tax_rate_merged = self.config['rename_merged_table']['Corporate Tax Rate (%)']
        self.col_country_merged = self.config['rename_merged_table']['Headquarters']

        self.col_revenue = self.config['columns']['largest_companies']['Revenue in (USD Million)']
        self.col_net_income = self.config['columns']['largest_companies']['Net Income in (USD Millions)']
        self.col_industry = self.config['columns']['largest_companies']['Industry']

    def compute(self):
        df = self.repo.merged_data.copy()

        col_gdp = df[self.col_gdp_merged]

        self.mean = col_gdp.mean()
        self.median = col_gdp.median()
        self.min = col_gdp.min()
        self.max = col_gdp.max()
        self.std = col_gdp.std()
        self.quantile = col_gdp.quantile([0.25, 0.5, 0.75])

    def get_biggest_sector(self):
        df = self.repo.largest_companies.copy()

        df['Profit Margin (%)'] = df[self.col_net_income] / df[self.col_revenue] * 100
        biggest_sector = df.groupby(self.col_industry, as_index=False)['Profit Margin (%)'].mean().sort_values(by = 'Profit Margin (%)', ascending = False)

        print(biggest_sector.head())
        return biggest_sector

    def get_tax_burden(self):
        df = self.repo.merged_data.copy()

        df['Tax Burden (%)'] = (df[self.col_tax_rate_merged] * df[self.col_revenue_merged] / df[self.col_gdp_merged] * 1000000) * 100

        return df[[self.col_country_merged, 'Tax Burden(%)']]

    def get_revenue_to_gdp(self):
        df = self.repo.merged_data.copy()

        df['Revenue to GDP (%)'] = df[self.col_revenue_merged]/(df[self.col_gdp_merged] * 1000000) * 100

        return df[[self.col_country_merged, 'Revenue to GDP (%)']]


if __name__ == '__main__':
    from constants import config_file
    from helpers import get_serialized_data
    import os

    config = get_serialized_data(os.path.join(os.getcwd(), config_file))
    repo = Repository(config=config, output_path = 'output')
    repo.get_data()

    model = Model(config = config, repo = repo)
    model.get_biggest_sector()







