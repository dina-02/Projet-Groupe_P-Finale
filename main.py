from etl import Etl, get_config
from view import plot_total_assets_by_country
from stats import summary_statistics_gdp


if __name__ == "__main__":
    config = get_config()

    etl = Etl(config=config, input_dir="input", sqlite_path="output/output.sqlite")

    etl.extract()
    etl.transform()
    etl.load()

    try:
        sorted_df = etl.sort_countries_by_total_assets()
        print("Pays triés par actifs totaux moyens (ordre décroissant) :")
        print(sorted_df)
    except Exception as e:
        print("Erreur lors du tri :", e)

print("Pays triés par actifs totaux moyens (ordre décroissant) :")
print(sorted_df)

plot_total_assets_by_country(sorted_df)

summary_statistics_gdp(sorted_df)
