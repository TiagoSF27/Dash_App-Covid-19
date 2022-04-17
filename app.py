from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)

df_country_vaccinations = pd.read_csv(r'https://github.com/TiagoSF27/Dash_App-Covid-19/datasets/country_vaccinations.csv')
df_country_vaccinations_by_manufacturer = pd.read_csv(r'https://github.com/TiagoSF27/Dash_App-Covid-19/datasets/country_vaccinations_by_manufacturer.csv')

country_options = [dict(label=country, value=country)
                   for country in df_country_vaccinations['country'].unique()]

country_options_manufacturer = [dict(label=country, value=country)
                                for country in df_country_vaccinations_by_manufacturer['location'].unique()]

country_dropdown = dcc.Dropdown(
                id='country_drop',
                options=country_options,
                multi=False,
                placeholder="Select a Country",
                persistence_type="session"
            )

country_manufacturer_dropdown = dcc.Dropdown(
                id='country_drop_manufacturer',
                options=country_options_manufacturer,
                multi=False,
                placeholder="Select a Country",
                persistence_type="session"
            )

radio_selection = dcc.RadioItems(
    id='radio_selection',
    options=[dict(label='Worldwide', value="worldwide"),
             dict(label='EU', value="eu")],
    value="worldwide"

)

slider_selection = dcc.Slider(
    id='slider_selection',
    min=1,
    max=6,
    marks={1: "2021-03-01", 2: "2021-06-01", 3: "2021-09-01",
           4: "2021-12-01", 5: "2022-03-01", 6: "Currently"},
    value=1,
    step=1
)

############################ df_country_vaccinations_by_manufacturer Clean-up ########################

# the dataframe "df_country_vaccinations_by_manufacturer" has multiple entries for each country
# as the dates move forward, the cumulative number of vaccines administered increases
# as such, we cannot simply sum all these values in a groupby
# we need the latest values for total_vaccinations, for each vaccine, for each country


# create a list with all the countries from "df_country_vaccinations_by_manufacturer"
# this list also contains values for the European Union, but we'll treat it like
# a country for now, since we want to keep that data as well
unique_location_list = df_country_vaccinations_by_manufacturer["location"].unique()

# create an empty list. We will store the indexes containing the latest "total_vaccinations" values here
# when this list is complete, we will use it to filter "df_country_vaccinations_by_manufacturer",
# ending up with a dataframe containing only useful information
vaccine_idx = []

for location in unique_location_list:
    # filter the full dataset to get a dataframe containing data of only one country
    # at a time from "unique_location_list"
    country = df_country_vaccinations_by_manufacturer.loc[
        df_country_vaccinations_by_manufacturer["location"] == location]

    # store in a list all the vaccines that were used in that country
    vaccines_used_in_country = list(country["vaccine"].unique())

    # check the dataframe for every last instance of each vaccine, to get the most up-to-date
    # "total_vaccinations" values. Then store the indexes of these instances

    for vaccine in vaccines_used_in_country:
        vaccine_idx.append(country.where(country == vaccine).last_valid_index())

# lastly, we are ready to filter the full dataset with these indexes.
# We now have the "total_vaccinations" values for every country
df_filtered = df_country_vaccinations_by_manufacturer.iloc[vaccine_idx]

# Now we need to separate the rows referring to the European Union, so we can use them for other visualizations
df_vaccine_manufacturer_EU = df_filtered.loc[df_filtered["location"] == "European Union"]
df_vaccine_manufacturer_countries = df_filtered.loc[df_filtered["location"] != "European Union"]

# This dataframe will be used for a horizontal bar plot containing the sum of all vaccine brands used
df_most_used_vaccines = pd.DataFrame(
    df_vaccine_manufacturer_countries.groupby("vaccine")["total_vaccinations"].sum().sort_values(ascending=True))

# This dataframe will be used for a horizontal bar plot containing the sum of all vaccine brands used only in the EU
df_most_used_vaccines_EU = pd.DataFrame(
    df_vaccine_manufacturer_EU.groupby("vaccine")["total_vaccinations"].sum().sort_values(ascending=True))

############################## df_country_vaccinations Clean-up #########################################
# NOTE: for the line plot that we are going to create later on, we will use all the data in the
# df_country_vaccinations dataframe. However, for a few other visualizations, we will need a
# cleaned version of this dataframe, which is what this section of the code will handle.

# the dataframe "df_country_vaccinations" has multiple entries for each country
# as the dates move forward, the cumulative number of vaccines administered increases
# as such, we cannot simply sum all these values in a groupby
# we only need the most recent values for each country
# it's worth noting that the most updated records for each country don't exactly
# share the same date, so we can't simply filter with one date value


# create a list with all the countries from "df_country_vaccinations"
# (223 countries)
unique_country_list = df_country_vaccinations["country"].unique()

# create an empty list. We will store the indexes containing the latest "date" values here
# when this list is complete, we will use it to filter "df_country_vaccinations",
# ending up with a dataframe containing only useful information
country_idx = []

for country in unique_country_list:
    country_idx.append(df_country_vaccinations.where(df_country_vaccinations == country).last_valid_index())

# lastly, we are ready to filter the full dataset with these indexes.
# We now have the most up-to-date values for every country
df_filtered_country_vaccinations = df_country_vaccinations.iloc[country_idx]

############################################# Layout #####################################################
app.layout = html.Div([

    html.Div([
        html.H1('Covid-19 Dashboard'),
    ], id='1st_row_FULL'),

    html.Div([
        html.Div([
            html.Label('History of Vaccination'),
            html.Br(),
            country_dropdown,
            html.Br(),
            dcc.Graph(id="line-charts-x-graph"),
        ], id="2nd_row_line_plot", style={'width': '50%'}, className='pretty_box'),

        html.Div([
            html.Label("People Vaccinated (%):"),
            html.Label(id='panel_1', className='pretty_box'),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Label("People Fully Vaccinated (%):"),
            html.Label(id='panel_2', className='pretty_box'),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Label("Number of People Vaccinated:"),
            html.Label(id='panel_3', className='pretty_box'),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Label("Total Vaccinations:"),
            html.Label(id='panel_4', className='pretty_box'),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Label("Most Vaccinated Countries in the World:"),
            html.Br(),
            slider_selection,
            html.Br(),
            dash_table.DataTable(id="most_vaccinated_countries")
        ], id="2nd_row_info_panels", style={'width': '50%'}, className='pretty_box'),

    ], id="2nd_row_FULL", style={'display': 'flex'}, className='pretty_box'),

    html.Div([
        html.Div([
            html.Label('Vaccination Manufacturers'),
            html.Br(),
            country_manufacturer_dropdown,
            html.Br(),
            dcc.Graph(id="bar-charts-x-graph"),
            html.Br(),
        ], id="3rd_row_bar_plot", style={'width': '40%'}, className='pretty_box'),

        html.Div([
            html.Label("Most Used Vaccines:"),
            html.Br(),
            radio_selection,
            html.Br(),
            dcc.Graph(id="most_used_vaccines"),
            html.Br(),
        ], id="3rd_row_vaccine_bar_plot", style={'width': '60%'}, className='pretty_box'),

    ], id='3rd_row_FULL', style={'display': 'flex'}, className='pretty_box'),

    html.Div([
        html.Div([
            html.P(['Group 40:', html.Br(),
                    'Tiago Ferreira, 20211317; Afonso Charrua, 20210991; ', html.Br(),
                    'Filipa Guimarães, 20210759; Ricardo Arraiano, 20210995'],
                   style={'font-size': '14px'}),
        ], style={'width': '60%'}),
        html.Div([
            html.P(['Sources: ',
                    html.Br(),
                    html.A('COVID-19 World Vaccination Progress',
                           href='https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress',
                           target='_blank')], style={'font-size': '14px'})
        ], style={'width': '40%'}),


    ], id='4th_row_FULL', style={'display': 'flex'}, className='pretty_box'),
])


@app.callback(
    Output("line-charts-x-graph", "figure"),
    Input("country_drop", "value")
)
def build_line_chart(country_drop):
    df_line_chart_dropdown_filter = df_country_vaccinations.loc[(df_country_vaccinations["country"] == country_drop)]
    fig = px.line(df_line_chart_dropdown_filter, x="date", y="total_vaccinations", color="country")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    return fig


@app.callback(
    Output("bar-charts-x-graph", "figure"),
    Input("country_drop_manufacturer", "value")
)
def build_bar_chart(country_drop):
    # filter the full dataset to get a dataframe containing only data of the country in "country_drop"
    df_bar_chart_dropdown_filter = df_vaccine_manufacturer_countries.loc[
        df_vaccine_manufacturer_countries["location"] == country_drop]

    fig = go.Figure(go.Bar(x=df_bar_chart_dropdown_filter["vaccine"],
                           y=df_bar_chart_dropdown_filter["total_vaccinations"],
                           text=df_bar_chart_dropdown_filter['total_vaccinations'],
                           ))
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.02,
                          xanchor="right",
                          x=1
                      ))

    return fig


@app.callback(
        Output("panel_1", "children"),
        Output("panel_2", "children"),
        Output("panel_3", "children"),
        Output("panel_4", "children"),
        Input("country_drop", "value"),
)
def build_panel(country_drop):
    df_panel_dropdown_filter = df_filtered_country_vaccinations.loc[
        (df_filtered_country_vaccinations["country"] == country_drop)]

    percent_people_vaccinated = df_panel_dropdown_filter["people_vaccinated_per_hundred"]
    percent_people_fully_vaccinated = df_panel_dropdown_filter["people_fully_vaccinated_per_hundred"]
    people_vaccinated = df_panel_dropdown_filter["people_vaccinated"]
    total_vaccinations = df_panel_dropdown_filter["total_vaccinations"]

    return percent_people_vaccinated, percent_people_fully_vaccinated, \
        people_vaccinated, total_vaccinations


@app.callback(
    Output("most_used_vaccines", "figure"),
    Input("radio_selection", "value")
)
def horizontal_bar_chart(selection):
    if selection == 'worldwide':
        most_used_vaccines_bar_plot = go.Figure(go.Bar(
            x=df_most_used_vaccines["total_vaccinations"],
            y=df_most_used_vaccines.index,
            text=df_most_used_vaccines["total_vaccinations"],
            orientation='h'))
        most_used_vaccines_bar_plot.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        most_used_vaccines_bar_plot.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        return most_used_vaccines_bar_plot

    elif selection == 'eu':
        most_used_vaccines_EU_bar_plot = go.Figure(go.Bar(
            x=df_most_used_vaccines_EU["total_vaccinations"],
            y=df_most_used_vaccines_EU.index,
            text=df_most_used_vaccines_EU["total_vaccinations"],
            orientation='h'))
        most_used_vaccines_EU_bar_plot.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        most_used_vaccines_EU_bar_plot.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        return most_used_vaccines_EU_bar_plot


@app.callback(
    Output("most_vaccinated_countries", "data"),
    Input("slider_selection", "value")
)
def most_vaccinated_countries_table(selection):
    if selection == 1:
        df_sorted_full_vacc_2021_03_01 = df_country_vaccinations.loc[ \
            df_country_vaccinations["date"] == "2021-03-01"] \
            .sort_values("people_fully_vaccinated_per_hundred",
                         ascending=False).head(10)

        df_renamed_2021_03_01 = df_sorted_full_vacc_2021_03_01[
            ["country", "total_vaccinations", "people_vaccinated_per_hundred",
             "people_fully_vaccinated_per_hundred"]] \
            .rename(columns={"country": "Country", "total_vaccinations": "Total Vacc.",
                             "people_vaccinated_per_hundred": "People Vacc. %",
                             "people_fully_vaccinated_per_hundred": "People Fully Vacc. %"})

        return df_renamed_2021_03_01.to_dict('rows')

    if selection == 2:
        df_sorted_full_vacc_2021_06_01 = df_country_vaccinations.loc[ \
            df_country_vaccinations["date"] == "2021-06-01"] \
            .sort_values("people_fully_vaccinated_per_hundred",
                         ascending=False).head(10)

        df_renamed_2021_06_01 = df_sorted_full_vacc_2021_06_01[
            ["country", "total_vaccinations", "people_vaccinated_per_hundred",
             "people_fully_vaccinated_per_hundred"]] \
            .rename(columns={"country": "Country", "total_vaccinations": "Total Vacc.",
                             "people_vaccinated_per_hundred": "People Vacc. %",
                             "people_fully_vaccinated_per_hundred": "People Fully Vacc. %"})

        return df_renamed_2021_06_01.to_dict('rows')

    if selection == 3:
        df_sorted_full_vacc_2021_09_01 = df_country_vaccinations.loc[ \
            df_country_vaccinations["date"] == "2021-09-01"] \
            .sort_values("people_fully_vaccinated_per_hundred",
                         ascending=False).head(10)

        df_renamed_2021_09_01 = df_sorted_full_vacc_2021_09_01[
            ["country", "total_vaccinations", "people_vaccinated_per_hundred",
             "people_fully_vaccinated_per_hundred"]] \
            .rename(columns={"country": "Country", "total_vaccinations": "Total Vacc.",
                             "people_vaccinated_per_hundred": "People Vacc. %",
                             "people_fully_vaccinated_per_hundred": "People Fully Vacc. %"})

        return df_renamed_2021_09_01.to_dict('rows')

    if selection == 4:
        df_sorted_full_vacc_2021_12_01 = df_country_vaccinations.loc[ \
            df_country_vaccinations["date"] == "2021-12-01"] \
            .sort_values("people_fully_vaccinated_per_hundred",
                         ascending=False).head(10)

        df_renamed_2021_12_01 = df_sorted_full_vacc_2021_12_01[
            ["country", "total_vaccinations", "people_vaccinated_per_hundred",
             "people_fully_vaccinated_per_hundred"]] \
            .rename(columns={"country": "Country", "total_vaccinations": "Total Vacc.",
                             "people_vaccinated_per_hundred": "People Vacc. %",
                             "people_fully_vaccinated_per_hundred": "People Fully Vacc. %"})

        return df_renamed_2021_12_01.to_dict('rows')

    if selection == 5:
        df_sorted_full_vacc_2022_03_01 = df_country_vaccinations.loc[ \
            df_country_vaccinations["date"] == "2022-03-01"] \
            .sort_values("people_fully_vaccinated_per_hundred",
                         ascending=False).head(10)

        df_renamed_2022_03_01 = df_sorted_full_vacc_2022_03_01[
            ["country", "total_vaccinations", "people_vaccinated_per_hundred",
             "people_fully_vaccinated_per_hundred"]] \
            .rename(columns={"country": "Country", "total_vaccinations": "Total Vacc.",
                             "people_vaccinated_per_hundred": "People Vacc. %",
                             "people_fully_vaccinated_per_hundred": "People Fully Vacc. %"})

        return df_renamed_2022_03_01.to_dict('rows')

    if selection == 6:
        df_sorted_currently = df_filtered_country_vaccinations. \
            sort_values("people_fully_vaccinated_per_hundred", ascending=False).head(10)

        df_renamed_currently = df_sorted_currently[
            ["country", "total_vaccinations", "people_vaccinated_per_hundred",
             "people_fully_vaccinated_per_hundred"]] \
            .rename(columns={"country": "Country", "total_vaccinations": "Total Vacc.",
                             "people_vaccinated_per_hundred": "People Vacc. %",
                             "people_fully_vaccinated_per_hundred": "People Fully Vacc. %"})

        return df_renamed_currently.to_dict('rows')


if __name__ == "__main__":
    app.run_server(debug=True)
