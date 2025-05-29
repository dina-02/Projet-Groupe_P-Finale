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

    def set_model(self, model):
        self.model = model

    def plot_roa_vs_efficiency(self, df):

        fig = px.scatter(
            df,
            x=self.config['firms_financial_summary_table']['asset_efficiency'],
            y=self.config['firms_financial_summary_table']['return_on_assets'],
            text=self.config['columns']['largest_companies']['Company'],
            title=self.config['plot_roa_vs_efficiency']['title'],
            labels=self.config['plot_roa_vs_efficiency']['labels']
        )
        #voir si j'ai la patience
        fig.update_traces(marker=dict(size=10, color='green', opacity=0.7), textposition='top right')
        fig.update_layout(width=900, height=600, title_font_size=18)
        st.plotly_chart(fig)

    def plot_top10_roa(self):
        df=self.model.get_firms_financial_summary()
        df=df.sort_values(by=self.model.return_on_assets, ascending=False).head(10).round(2)  #arrorndi car illisible

        fig = px.bar(
            df,
            x=self.config['firms_financial_summary_table']['company'],
            y=self.config['firms_financial_summary_table']['return_on_assets'],
            title=self.config['plot_top10_roa']['title'],
            labels=self.config['plot_top10_roa']['labels'],
            text=self.config['plot_top10_roa']['col_y']
        )

        fig.update_traces(marker_color='indigo', textposition='outside')
        fig.update_layout(width=800, height=500)
        st.plotly_chart(fig)

    def plot_contribution_vs_roa(self):

        df=self.model.get_country_financial_summary()

        fig = px.scatter(
            df,
            x=self.config['countries_financial_summary_table']['average_contrib_to_pub_fin'],
            y=self.config['countries_financial_summary_table']['average_roa'],
            text=self.config['plot_contribution_vs_roa']['text'],
            title=self.config['plot_contribution_vs_roa']['title'],
            labels=self.config['plot_contribution_vs_roa']['labels']
        )
        fig.update_traces(marker=dict(size=12, color='darkred'), textposition='top center')
        fig.update_layout(width=800, height=600)
        st.plotly_chart(fig)

        st.markdown(self.config['plot_contribution_vs_roa']['markdown'])

    def plot_macro_correlation_heatmap(self):

        df = self.model.get_country_financial_summary()
        df = df.set_index(self.model.col_country_merged)
        corr_df= df.corr()

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
            title=self.config['plot_macro_correlation_heatmap']['title'],
            width=700,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(self.config['plot_macro_correlation_heatmap']['markdown'])

