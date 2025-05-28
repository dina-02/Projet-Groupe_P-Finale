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

        data = self.config['data']

        selected_dataset = st.sidebar.radio(
            self.streamlit_widgets_config['ticker_radio']['label'],
            list(data.keys())
        )

        chart_type = st.sidebar.radio(
            "Choix du graphique",
            self.streamlit_widgets_config['ticker_radio']['items']
        )

        st.subheader(f"{selected_dataset} - Visualisation des données")

        # Gérer l'état du bouton pour ne pas réinitialiser à chaque interaction (ça faisait un bug dans le filtrage streamlit quittait)
        if 'go_clicked' not in st.session_state:
            st.session_state.go_clicked = False

        if st.button("Afficher"):
            st.session_state.go_clicked = True

        if st.session_state.go_clicked:
            if selected_dataset == "get_new_table":
                df = self.model.get_new_table()
                with st.expander("Tableau - Données par pays"):
                    st.dataframe(df)

            elif selected_dataset == "get_another_new_table":
                df = self.model.get_another_new_table()
                with st.expander("Tableau - Données par entreprise"):
                    st.dataframe(df)

                if chart_type == "ROA vs Efficiency":
                    seuil_roa = st.slider("Filtrer ROA max", 0, 6000, 1000)
                    seuil_eff = st.slider("Filtrer efficacité max", 0, 6000, 1000)

                    df_plot = self.model.get_roa_vs_efficiency()
                    df_plot = df_plot[
                        (df_plot['Return on Assets'] <= seuil_roa) &
                        (df_plot['Asset Efficiency'] <= seuil_eff)
                    ]

                    self.view.plot_roa_vs_efficiency(df_plot)

if __name__ == "__main__":
    app = Main()
    app.run()
