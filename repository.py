import os.path
import pandas as pd

from constants import config_file, output_path
from helpers import get_serialized_data


def get_config():
    """
    Load and return the project configuration from the config file.
    :return: Dictionary with configuration data.
    """

    config_full_path = os.path.join(os.getcwd(), config_file)
    return get_serialized_data(config_full_path)

class Repository:
    """
    Handles loading data either from CSV files or (optionally) a database.

    This class centralizes the logic to retrieve the project's data.
    """

    def __init__(self, config: dict, output_path: str = None) -> None:
        """
        Initialize the Repository with the configuration and data source paths.

        :param config: Configuration dictionary.
        :param output_path: Path to the folder where CSV files are stored.
        """

        self.config = config
        self.output_path = output_path
        self.merged_data = None
        self.largest_companies = None

    def get_data(self) -> None:
        """
        Load datasets from CSV files defined in the configuration.

        This method fills `self.merged_data` and `self.largest_companies`
        with DataFrames read from the specified CSV files.
        :return: none
        """

        merged_file = os.path.join(self.output_path, self.config['files_csv']['merged_table'])
        largest_file = os.path.join(self.output_path, self.config['files_csv']['source_largest_companies'])

        self.merged_data = pd.read_csv(merged_file, sep=',')
        self.largest_companies = pd.read_csv(largest_file,sep =',')

if __name__ == '__main__':
    config_path = os.path.join(os.getcwd(), config_file)
    config = get_serialized_data(config_path)
    repo = Repository(config, output_path)
    repo.get_data()

    print(repo.merged_data.head())
    print(repo.largest_companies.head())