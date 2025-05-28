import os.path
import pandas as pd
from sqlalchemy import create_engine

##marche

class Repository:
    def __init__(self, config: dict, database_path: str = None, output_path: str = None) -> None:
        self.config = config
        self.database_path = database_path
        self.output_path = output_path
        self.merged_data = None
        self.largest_companies = None

    def get_data(self) -> None:
        if self.config['etl_main_parameters']['to_sqlite']:
            engine = create_engine(f'sqlite:///{self.database_path}', echo = True)
            self.merged_data = pd.read_sql_table(self.config['files_sql']['merged_table'], engine)
            self.largest_companies = pd.read_sql(self.config['files_sql']['source_largest_companies'], engine)

        elif self.config['etl_main_parameters']['to_csv']:
                merged_file = os.path.join(self.output_path, self.config['files_csv']['merged_table'])
                largest_file = os.path.join(self.output_path, self.config['files_csv']['source_largest_companies'])

                self.merged_data = pd.read_csv(merged_file, sep = ',')
                self.largest_companies = pd.read_csv(largest_file, sep = ',')

if __name__ == '__main__':
    import os
    from helpers import get_serialized_data
    from constants import config_file

    config_path = os.path.join(os.getcwd(), config_file)
    config = get_serialized_data(config_path)

    repo = Repository(config=config, output_path = 'output', database_path = 'output/output.sqlite')

    repo.get_data()

    print(repo.merged_data.head())

    print(repo.largest_companies.head())



