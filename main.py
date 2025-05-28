

from etl import Etl, get_config
from view import plot_total_assets_by_country

if __name__ == "__main__":
    config = get_config()
    etl = Etl(config=config, input_dir="input", sqlite_path="output/output.sqlite")

    etl.extract()
    etl.transform()
    etl.load()

    sorted_df = etl.sort_countries_by_total_assets()
    plot_total_assets_by_country(sorted_df)
