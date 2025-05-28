import os.path
import pandas as pd
from sqlalchemy import create_engine
from helpers import get_serialized_data
from constants import config_file

##marche

def get_config():
    """
    Load and return the project configuration from the config file.
    :return: the serialized data
    """

    config_full_path = os.path.join(os.getcwd(), config_file)
    return get_serialized_data(config_full_path)

class Repository:
    """
    A class used to load data either from a SQLite database or CSV files,
    depending on the project settings.
    """

    def __init__(self, config: dict, database_path: str = None, output_path: str = None) -> None:
        """
        Initialize the Repository with config and data source paths.

        :param config: dictionary with settings and file names
        :param database_path: path to the SQLite database
        :param output_path: path to the CSV files folder
        """

        self.config = config
        self.database_path = database_path
        self.output_path = output_path
        self.merged_data = None
        self.largest_companies = None

    def get_data(self) -> None:
        """
        Load data from the source defined in the configuration.
        Either reads from a SQLite database or from CSV files.
        :return: none
        """

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
