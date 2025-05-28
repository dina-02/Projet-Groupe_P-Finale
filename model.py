import pandas as pd
from repository import Repository

class Model:
    def __init__(self, config, repo):
        self.config = config
        self.repo = repo

    def get_biggest_sector(self):
        df = self.repo.largest_companies.copy()

        df['Profit Margin (%)'] = df['Net Income in (USD Millions)'] / df['Revenue in (USD Million)'] * 100
        biggest_sector = df.groupby('Industry', as_index=False)['Profit Margin (%)'].mean().sort_values(by = 'Profit Margin (%)', ascending = False)

        print(biggest_sector.head())
        return biggest_sector

    ####

if __name__ == '__main__':
    from constants import config_file
    from helpers import get_serialized_data
    import os

    config = get_serialized_data(os.path.join(os.getcwd(), config_file))
    repo = Repository(config=config, output_path = 'output')
    repo.get_data()

    model = Model(config = config, repo = repo)
    model.get_biggest_sector()





