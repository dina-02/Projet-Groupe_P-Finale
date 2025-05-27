import seaborn as sns
import matplotlib.pyplot as plt

def plot_total_assets_by_country(df):
    """
    Affiche le graphique (à finir).
    """

    df_sorted = df.sort_values("Mean Total Assest in (USD Millions)", ascending=False)

    top_15 = df_sorted.head(15)

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=top_15,
        x="Headquarters",
        y="Mean Total Assest in (USD Millions)",
        palette="Blues",
        alpha=0.8
    )

    plt.title("Mean Total Assets in (USD Millions) Per Countries", fontsize=14)
    plt.xlabel("Countries (Headquarters)")
    plt.ylabel("Mean Total Assets in (millions USD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
