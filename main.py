import streamlit as st
import os
from model import Model
from constants import config_file
from repository import get_config, Repository
from view import View

class Main:
    def __init__(self):
        self.config = get_config()
        self.streamlit_config = self.config['streamlit']
        self.streamlit_widgets_config = self.streamlit_config["widgets"]

        self.view = View(self.config)
        self.repo = Repository(self.config, None, 'output')
        self.model = Model(self.config, self.repo)
        self.view.set_repository(self.repo)

    def run(self):
        self.repo.get_data()
        df_get_new_table = self.model.get_new_table()
        df_get_another_new_table = self.model.get_another_new_table()

        data = self.config['data']

        selected_dataset = st.sidebar.radio(
            self.streamlit_widgets_config['ticker_radio']['label'], data.keys()
        )

        dataset_info = data[selected_dataset]

        chart_type = st.sidebar.radio(
            self.streamlit_widgets_config['ticker_radio']['label'],
            self.streamlit_widgets_config['ticker_radio']['items']
        )

        st.subheader(
            self.streamlit_widgets_config["title"]["label"].format(
                selected_dataset, dataset_info
            )
        )

        go = st.button(self.streamlit_widgets_config["start_button"]["label"])

        if go:

            # if selected_dataset == 'merged_table':
            #     df_plot = self.model.get_inflation_vs_interest()
            #     self.view.plotly_inflation_vs_interest(df_plot)
            #
            # exp_df = st.expander(
            #     self.streamlit_widgets_config["expander_data"]["label"]
            # )
            # with st.expander('je commence a fatiguer la'): ##
            #     st.dataframe(df_merged)

            if selected_dataset == 'get_new_table':
                df = self.model.get_new_table()
                with st.expander('new test'):
                    st.dataframe(df)

            elif selected_dataset == 'get_another_new_table':
                df= self.model.get_another_new_table()

            # exp_df = st.expander(
            #     self.streamlit_widgets_config["expander_data"]["label"]
            # )
                with st.expander('new test'):
                    st.dataframe(df)






if __name__ == "__main__":
    app = Main()
    app.run()
