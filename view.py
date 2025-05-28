import streamlit as st
import mplfinance as mpf
import matplotlib.pyplot as plt

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

    def plot_inflation_vs_interest(self, df):
        fig, ax = plt.subplots()
        ax.scatter(df[df.columns[0]], df[df.columns[1]], color='blue', marker='o')

        ax.set_xlabel("Inflation Rate (%)")
        ax.set_ylabel("Interest Rate (%)")
        ax.set_title("Relation entre inflation et taux d’intérêt")

        for i, label in enumerate(df[df.columns[2]]):
            ax.annotate(label, (df.iloc[i, 0], df.iloc[i, 1]), fontsize=8)

        st.pyplot(fig)
