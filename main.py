import logging
import streamlit as st

from logger import Logger
from etl import ETL
from model import Model
from view import View
from constants import output_path, database_path, input_dir
from repository import get_config, Repository

config = get_config()


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
        Logger(self.config).set_log()
        logging.info('initializing')

        etl = ETL(config=config, input_dir=input_dir)
        etl.run()
        logging.info('ETL completed')

        self.repo = Repository(self.config, output_path)
        self.repo.get_data()
        logging.info('Data loaded')

        self.model = Model(self.config, self.repo)
        self.model.export_datasets_toSQLite(database_path)
        logging.info('Data exported to SQLite')

        self.view = View(self.config)
        self.view.set_model(self.model)

        # Store specific config sections for UI elements
        self.streamlit_config = self.config['streamlit']
        self.streamlit_widgets_config = self.streamlit_config["widgets"]


    def run(self) -> None:
        """
        Run the Streamlit application.

        Handles user input via sidebar and UI widgets, loads data using the repository,
        and renders appropriate charts and tables based on the selected options.
        :return: none
        """

        data = self.streamlit_widgets_config['options']   # Available datasets for selection

        # Sidebar radio button for dataset choice
        selected_dataset = st.sidebar.radio(
            self.streamlit_widgets_config['selected_dataset']['label'],
            list(data.keys())
        )

        # Display the header with selected dataset
        st.subheader(f"{selected_dataset} - {self.streamlit_widgets_config['header']['label']}",
                     divider=self.streamlit_widgets_config['header']['divider'])

        # Create two columns for chart selection and execution
        col1, col2 = st.columns(2, vertical_alignment=self.streamlit_widgets_config['column']['vertical_alignment'])

        # First column: chart type selection
        with col1:
            chart_type = st.selectbox(
                self.streamlit_widgets_config['select_box']['label'],
                self.streamlit_widgets_config['options'][selected_dataset]
            )

        # Second column: display trigger
        with col2:
            if 'go_clicked' not in st.session_state:
                st.session_state.go_clicked = False   # Initialize session flag

            if st.button(self.streamlit_widgets_config['start_button']['label']):
                st.session_state.go_clicked = True   # Trigger display

        st.divider()   # Visual separation

        if st.session_state.go_clicked:

            # If dataset is country-level
            logging.info(f'button clicked: {selected_dataset} and {chart_type}')
            if selected_dataset == "Données par pays":
                df = self.model.get_country_financial_summary()

                with st.expander(self.streamlit_widgets_config['expander']['donnees_par_pays'], expanded=False):
                    st.dataframe(df)   # Show data table

                st.divider()

                # Country-level visualizations
                if chart_type == "Contribution vs ROA":
                    self.view.plot_contribution_vs_roa()
                    logging.info('displayed chart: Contribution vs ROA')
                elif chart_type == "Matrice de corrélation macro":
                    self.view.plot_macro_correlation_heatmap()
                    logging.info('displayed chart: Matrice de corrélation macro')

            # If dataset is firm-level
            elif selected_dataset == "Données par entreprise":
                df = self.model.get_firms_financial_summary()

                with st.expander(self.streamlit_widgets_config['expander']['donnees_par_entreprise'], expanded=False):
                    st.dataframe(df)   # Show data table

                st.divider()

                # Company-level visualizations
                if chart_type == "ROA vs Efficiency":

                    # Sliders to filter the scatter plot
                    threshold_roa = st.slider(self.streamlit_widgets_config['slider']['roa'],
                                              min_value=0.5, max_value=3.1, value=1.5, step=0.1)

                    threshold_eff = st.slider(self.streamlit_widgets_config['slider']['efficiency'],
                                              min_value=0.5, max_value=5.1, value=3.0, step=1.0)

                    logging.info(f'filtering firms with ROA <= {threshold_roa} and Efficiency <= {threshold_eff}')

                    df_plot = self.model.get_firms_financial_summary()
                    df_plot = df_plot[
                        (df_plot[self.model.return_on_assets] <= threshold_roa) &
                        (df_plot[self.model.asset_efficiency] <= threshold_eff)
                    ]

                    self.view.plot_roa_vs_efficiency(df_plot)
                    logging.info('displayed chart: Plot vs ROA efficiency')

                elif chart_type == "Top 10 ROA":
                    self.view.plot_top10_roa()
                    logging.info('displayed chart: Plot Top10 ROA')


# Application execution entry point
if __name__ == '__main__':
    app = Main()
    app.run()