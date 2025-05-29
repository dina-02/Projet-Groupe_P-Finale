import streamlit as st
import plotly.express as px


class View:
    def __init__(self, config: dict):
        self.config = config
        self.streamlit_settings = self.config['streamlit']['settings']

        st.set_page_config(
            page_title=self.streamlit_settings['page_title'],
            # page_icon=self.streamlit_settings['page_icon']
            initial_sidebar_state=self.streamlit_settings['initial_sidebar_state'],
            # menu_items=self.streamlit_settings['menu_items']
        )

        self.repo = None
        self.model = None
        self.fig = None
        self.ax = None

    def set_repository(self, repo):
        self.repo = repo

    def compute_chart(self, chart_type: str):
        st.bar_chart(self.repo.merged_data.set_index('Country'))

    ## à continuer pour l'export

    def plotly_inflation_vs_interest(self, df):
        fig = px.scatter(
            df,
            x=df.columns[0],  # Inflation
            y=df.columns[1],  # Interest
            text=df.columns[2],  # Country
            title="Relation entre inflation et taux d’intérêt",
            labels={
                df.columns[0]: "Inflation Rate (%)",
                df.columns[1]: "Interest Rate (%)"
            }
        )
        fig.update_traces(marker=dict(size=12, color='blue'), textposition='top center')
        fig.update_layout(width=700, height=500)

        st.plotly_chart(fig)

    def plot_roa_vs_efficiency(self, df):
        fig = px.scatter(
            df,
            x='Asset Efficiency',
            y='Return on Assets',
            text=self.config['columns']['largest_companies']['Company'],
            title='Rentabilité vs Efficacité des actifs (entreprises)',
            labels={
                'Asset Efficiency': 'Efficacité des Actifs',
                'Return on Assets': 'ROA (%)'
            }
        )
        fig.update_traces(marker=dict(size=10, color='green', opacity=0.7), textposition='top right')
        fig.update_layout(width=900, height=600, title_font_size=18)
        st.plotly_chart(fig)

    def plot_top10_roa(self, df):
        df["ROA arrondi"] = df["Return on Assets"].round(2)  #Arrondi car illisible sur streamlit sinon (trop de chiffres après la virgule)

        fig = px.bar(
            df,
            x=self.config['columns']['largest_companies']['Company'],
            y="ROA arrondi",
            title='Top 10 entreprises par ROA',
            labels={"ROA arrondi": "ROA (%)"},
            text="ROA arrondi"
        )
        fig.update_traces(marker_color='indigo', textposition='outside')
        fig.update_layout(width=800, height=500)
        st.plotly_chart(fig)

    def plot_contribution_vs_roa(self, df):
        fig = px.scatter(
            df,
            x="Average Contribution to Public Finances (% of GDP)",
            y="Average ROA",
            text="Country",
            title="ROA moyen vs Contribution publique par pays",
            labels={
                "Average Contribution to Public Finances (% of GDP)": "Contribution publique (% PIB)",
                "Average ROA": "ROA moyen (%)"
            }
        )
        fig.update_traces(marker=dict(size=12, color='darkred'), textposition='top center')
        fig.update_layout(width=800, height=600)
        st.plotly_chart(fig)

        st.markdown("Ce graphique permet de visualiser les différences de modèles économiques entre pays. On observe que certains pays comme la Chine ou les États-Unis bénéficient de champions nationaux très rentables mais peu taxés, tandis que la France semble illustrer un modèle économique redistributif dans lequel des entreprises peu rentables soutiennent malgré tout significativement les recettes publiques. Cela met en évidence des arbitrages entre efficacité économique et politique fiscale.")

    def plot_macro_correlation_heatmap(self, corr_df):
        fig = px.imshow(
            corr_df,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            labels=dict(color="Corrélation"),
            aspect="auto"
        )
        fig.update_layout(
            title="Matrice de corrélation entre indicateurs macroéconomiques",
            xaxis_title="",
            yaxis_title="",
            width=700,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Interprétation des coefficients :**  
        - **Revenue to GDP (%) vs Contribution Publique (% PIB) : +0.90** ➤ Des entreprises plus présentes dans l’économie génèrent logiquement plus de recettes fiscales pour l’État.  

        - **Taux d’intérêt réel vs ROA moyen : -0.44** ➤ Lorsque les taux d’intérêt réels sont élevés, les entreprises ont tendance à être moins rentables : taux réel élevé plus lourd ➤ coût du crédit plus lourd ➤ moins d'investissement et de croissance ➤ ROA plus faible.  

        - **Real Interest Rate (%) vs Revenue to GDP (%) ou Contribution Publique : corrélations proches de 0** ➤ Il n’y a pas de lien direct entre les taux d’intérêt réels et la taille des entreprises dans l’économie (ou leur contribution fiscale).
        """)






