import streamlit as st
import mplfinance as mpf

class View:
    def __init__(self,config: dict):
        self.config = config
        self.streamlit_settings = self.config['streamlit']['settings']

        st.set_page_config(
            page_title=self.streamlit_settings['page_title'],
            #page_icoon=self.streamlit_settings['page_icon']
            initial_sidebar_state=self.streamlit_settings['initial_sidebar_state'],
            #menu_items=self.streamlit_settings['menu_items']
        )

        self.repo = None
        self.model = None
        self.fig = None
        self.ax = None

    def set_repository(self, repo):
        self.repo = repo

    def compute_chart(self, chart_type: str):
        st.bar_chart(self.repo.merged_data.set_index('Country'))

    ## a continuer pour l'export


