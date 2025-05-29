import streamlit as st

from etl import ETL
from model import Model
from constants import output_path
from repository import get_config, Repository
from view import View


class Main:
    """
    Main entry point of the Streamlit application.

    This class is responsible for loading configuration, initializing the Repository, Model, and View,
    and managing user interaction through the Streamlit UI to display financial summaries and visualizations.
    """

    def __init__(self):
        """
        Initialize the application components: configuration, repository, model, and view.
        """

        self.config = get_config()
        self.repo = Repository(self.config, output_path)
        self.model = Model(self.config, self.repo)
        self.view = View(self.config)
        self.view.set_model(self.model)

        self.streamlit_config = self.config['streamlit']
        self.streamlit_widgets_config = self.streamlit_config["widgets"]

    def run(self):
        """
        Run the Streamlit application.

        Handles user input via sidebar and UI widgets, loads data using the repository,
        and renders appropriate charts and tables based on the selected options.
        :return: none
        """

        self.repo.get_data()

        data = self.streamlit_widgets_config['options']

        selected_dataset = st.sidebar.radio(
            self.streamlit_widgets_config['selected_dataset']['label'],
            list(data.keys())
        )

        st.subheader(f"{selected_dataset} - {self.streamlit_widgets_config['header']['label']}",
                     divider=self.streamlit_widgets_config['header']['divider'])

        col1, col2 = st.columns(2, vertical_alignment=self.streamlit_widgets_config['column']['vertical_alignment'])

        with col1:
            chart_type = st.selectbox(
                self.streamlit_widgets_config['select_box']['label'],
                self.streamlit_widgets_config['options'][selected_dataset]
            )

        with col2:
            if 'go_clicked' not in st.session_state:
                st.session_state.go_clicked = False

            if st.button(self.streamlit_widgets_config['start_button']['label']):
                st.session_state.go_clicked = True

        st.divider()

        if st.session_state.go_clicked:

            if selected_dataset == "Données par pays":
                df = self.model.get_country_financial_summary()

                with st.expander(self.streamlit_widgets_config['expander']['donnees_par_pays'], expanded=False):
                    st.dataframe(df)

                st.divider()

                if chart_type == "Contribution vs ROA":
                    self.view.plot_contribution_vs_roa()
                elif chart_type == "Matrice de corrélation macro":
                    self.view.plot_macro_correlation_heatmap()

            elif selected_dataset == "Données par entreprise":
                df = self.model.get_firms_financial_summary()

                with st.expander(self.streamlit_widgets_config['expander']['donnees_par_entreprise'], expanded=False):
                    st.dataframe(df)

                st.divider()

                if chart_type == "ROA vs Efficiency":
                    threshold_roa = st.slider(self.streamlit_widgets_config['slider']['roa'],
                                              min_value=0.5, max_value=3.1, value=1.0, step=0.1)

                    threshold_eff = st.slider(self.streamlit_widgets_config['slider']['efficiency'],
                                              min_value=0.5, max_value=5.1, value=1.5, step=1.0)

                    df_plot = self.model.get_firms_financial_summary()
                    df_plot = df_plot[
                        (df_plot[self.model.return_on_assets] <= threshold_roa) &
                        (df_plot[self.model.asset_efficiency] <= threshold_eff)
                    ]

                    self.view.plot_roa_vs_efficiency(df_plot)

                elif chart_type == "Top 10 ROA":
                    self.view.plot_top10_roa()


if __name__ == "__main__":
    app = Main()
    app.run()
