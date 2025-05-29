import streamlit as st
import plotly.express as px
import pandas as pd


class View:
    """
    Handles all visualizations for the Streamlit app, using Plotly charts.

    This class manages setting up the Streamlit page configuration and provides
    methods to display various financial charts based on country and firm data.
    """

    def __init__(self, config: dict):
        """
         Initializes the View with the given configuration and sets Streamlit page settings.
        :param config: A dictionary containing the application's configuration settings.
        """

        self.config = config
        self.streamlit_settings = self.config['streamlit']['settings']

        # Set the global page configuration using Streamlit
        st.set_page_config(
            page_title=self.streamlit_settings['page_title'],
            layout=self.streamlit_settings['layout'],
            initial_sidebar_state=self.streamlit_settings['initial_sidebar_state'],
            menu_items=self.streamlit_settings['menu_items']
        )

        # Initialize placeholders for external objects
        self.repo = None
        self.model = None
        self.fig = None
        self.ax = None

    def set_repository(self, repo) -> None:
        """
        Links the repository instance to the view.

        :param repo: Repository object providing access to data.
        :return: none
        """

        self.repo = repo

    def set_model(self, model) -> None:
        """
        Links the model instance to the view.

        :param model: Model object providing processed financial data.
        :return: none
        """

        self.model = model

    def plot_roa_vs_efficiency(self, df: pd.DataFrame) -> None:
        """
         Displays a scatter plot of Return on Assets vs. Asset Efficiency for firms.

        :param df: DataFrame containing company data with ROA and efficiency metrics.
        :return: none
        """

        # Create scatter plot with Plotly
        fig = px.scatter(
            df,
            x=self.config['firms_financial_summary_table']['asset_efficiency'],
            y=self.config['firms_financial_summary_table']['return_on_assets'],
            text=self.config['columns']['largest_companies']['Company'],
            title=self.config['plot_roa_vs_efficiency']['title'],
            labels=self.config['plot_roa_vs_efficiency']['labels']
        )
        # Customize marker appearance
        fig.update_traces(marker=dict(size=10, color='green', opacity=0.7), textposition='top right')
        fig.update_layout(width=900, height=600, title_font_size=18)

        # Render chart in Streamlit
        st.plotly_chart(fig)

        # Add custom explanatory markdown below the chart
        st.markdown(self.config['plot_roa_vs_efficiency']['markdown'])

    def plot_top10_roa(self) -> None:
        """
        Displays a bar chart of the top 10 companies ranked by Return on Assets.
        :return: none
        """

        # Get financial summary, sort by ROA, and select top 10
        df=self.model.get_firms_financial_summary()
        df=df.sort_values(by=self.model.return_on_assets, ascending=False).head(10).round(2)  #arrorndi car illisible

        # Create bar chart
        fig = px.bar(
            df,
            x=self.config['firms_financial_summary_table']['company'],
            y=self.config['firms_financial_summary_table']['return_on_assets'],
            title=self.config['plot_top10_roa']['title'],
            labels=self.config['plot_top10_roa']['labels'],
            text=self.config['plot_top10_roa']['col_y']
        )

        # Customize chart appearance
        fig.update_traces(marker_color='indigo', textposition='outside')
        fig.update_layout(width=800, height=500)

        # Show chart in Streamlit
        st.plotly_chart(fig)

        # Add markdown explanation if available
        st.markdown(self.config['plot_top10_roa']['markdown'])

    def plot_contribution_vs_roa(self) -> None:
        """
        Displays a scatter plot comparing average contribution to public finances vs. average ROA per country.
        :return: none
        """

        # Load summary data from the model
        df=self.model.get_country_financial_summary()

        # Create scatter plot
        fig = px.scatter(
            df,
            x=self.config['countries_financial_summary_table']['average_contrib_to_pub_fin'],
            y=self.config['countries_financial_summary_table']['average_roa'],
            text=self.config['plot_contribution_vs_roa']['text'],
            title=self.config['plot_contribution_vs_roa']['title'],
            labels=self.config['plot_contribution_vs_roa']['labels']
        )

        # Customize marker appearance
        fig.update_traces(marker=dict(size=12, color='darkred'), textposition='top center')
        fig.update_layout(width=800, height=600)

        # Display chart in Streamlit
        st.plotly_chart(fig)

        # Add markdown description
        st.markdown(self.config['plot_contribution_vs_roa']['markdown'])

    def plot_macro_correlation_heatmap(self) -> None:
        """
        Displays a heatmap of correlations between macroeconomic indicators for countries.
        :return: none
        """

        # Get country-level data and compute correlation matrix
        df = self.model.get_country_financial_summary()
        df = df.set_index(self.model.col_country_merged)
        corr_df= df.corr()

        # Create heatmap with Plotly
        fig = px.imshow(
            corr_df,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            labels=dict(color="Corrélation"),
            aspect="auto"
        )

        # Customize layout
        fig.update_layout(
            title=self.config['plot_macro_correlation_heatmap']['title'],
            width=700,
            height=600
        )

        # Render chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        # Add description below the chart
        st.markdown(self.config['plot_macro_correlation_heatmap']['markdown'])

