import streamlit as st
import mplfinance as mpf
import matplotlib.pyplot as plt
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

