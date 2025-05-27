import os.path

# class Repository:
#     def __init__(self, config: dict, database_path: str) -> None:
#         self.config = config
#         self.database_path = database_path
#         self.merged_data = None
#         self.largest_companies = None
#
#     def get_data(self) -> None:
#         ''''''
#         engine = create_engine(f'sqlite:///{self.database_path}', echo=True)
#
#
#         self.merged_data = pd.read_sql(self.config['files']['merged_table'], engine)
#         self.largest_companies = pd.read_sql(self.config['files']['source_largest_companies'], engine)
#
#         print(f'merged_data.shape = {self.merged_data.shape}')
#         print(f'largest_companies.shape = {self.largest_companies.shape}')
#
# if __name__ == "__main__":
#     import os
#     from helpers import get_serialized_data
#     from constants import config_file
#
#     config_path = os.path.join(os.getcwd(), config_file)
#     config = get_serialized_data(config_path)
#
#     repo = Repository(config=config, database_path="output/output.sqlite")
#
#     repo.get_data()
#
#     print(repo.merged_data.head())
#
#     print(repo.largest_companies.head())

import pandas as pd

class Repository:
    def __init__(self, config: dict, output_path: str) -> None:
        self.config = config
        self.output_path = output_path
        self.merged_data = None
        self.largest_companies = None

    def get_data(self) -> None:
        merged_file = os.path.join(self.output_path, self.config['files']['merged_table'])
        largest_file = os.path.join(self.output_path, self.config['files']['source_largest_companies'])

        #engine = create_engine(f"sqlite:///{self.sqlite_path}")
        self.merged_data = pd.read_csv(merged_file, sep=',')
        self.largest_companies = pd.read_csv(largest_file, sep=',')

        print(f"merged_data.shape = {self.merged_data.shape}")
        print(f"largest_companies.shape = {self.largest_companies.shape}")

if __name__ == "__main__":
    import os
    from helpers import get_serialized_data
    from constants import config_file

    config_path = os.path.join(os.getcwd(), config_file)
    config = get_serialized_data(config_path)

    repo = Repository(config=config, output_path="output")

    repo.get_data()

    print("✅ Merged table:")
    print(repo.merged_data.head(), end="\n\n")


