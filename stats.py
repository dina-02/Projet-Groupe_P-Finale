def summary_statistics_gdp(df):
    """
    Affiche les statistiques descriptives uniquement pour la colonne du PIB.
    """
    column = "GDP (USD Trillions)"

    print(f"\nRésumé statistique pour : {column}")
    print(f"- Moyenne : {df[column].mean()}")
    print(f"- Médiane : {df[column].median()}")
    print(f"- Minimum : {df[column].min()}")
    print(f"- Maximum : {df[column].max()}")
    print(f"- Écart-type : {df[column].std()}")
    print(f"- Quantiles :\n{df[column].quantile([0.25, 0.5, 0.75])}")
