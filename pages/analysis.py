import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input, State

from application.network_analysis import NetworkAnalysis
from application.youtube_api import YoutubeAPI
from server import app
from utilities.auth import layout_auth

success_alert = dbc.Alert(
    'Finished searching',
    color='success',
    dismissable=True
)

failure_alert = dbc.Alert(
    'Parameters are invalid',
    color='danger',
    dismissable=True
)

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='analysis-url', refresh=True, pathname='/analysis')

n = True


@layout_auth('require-authentication')
def layout():
    # if current_user.is_authenticated:
    return dbc.Row(
        dbc.Col(
            children=[
                location,
                html.Div(id='home-login-trigger', style=dict(display='none')),
                html.H3('Analyze YouTube Social Media'),
                html.Br(),
                html.H5('What the application does: '),
                html.Ul(
                    [
                        html.Li("Searches the YouTube platform for videos regarding the search keyword"),
                        html.Li("Downloads the necessary data from videos (title, description, comments and others)"),
                        html.Li("Creates a graph by representing the connections between users that commented on "
                                "selected videos"),
                        html.Li("Computes PageRank to determine the most important users"),
                        html.Li("Displays the created graph and the results from PageRank")
                    ]
                ),
                html.H5('To use the application, enter the keyword and the number of videos and click SEARCH'),
                html.Div(id='output-alert'),
                html.H5("Keyword: "),
                dcc.Input(id='keyword', value='', type='text', placeholder="keyword"),
                html.Br(), html.Br(),
                html.H5("Number of videos: "), html.Div(id="range-val"),
                dcc.Input(id='nr_videos', value='1', type='range', placeholder="Valid from 1 to 10", min=1, max=10,
                          step=1),
                html.Br(), html.Br(),
                dbc.Button('Search', color='primary', id='submit-button'),
                html.Br(), html.Br(),
                dcc.Loading(
                    id="loading-1",
                    type="graph",
                    children=html.Div(id="loading-output-1")
                ),
                html.Br(),
                html.Hr(),
                html.Br(),
                dbc.Col(html.Div(id='output-div'))
            ],
            align="center"
        ),
        justify="center"
    )


@app.callback(Output("range-val", "children"),
              [Input('nr_videos', 'value')])
def input_triggers_spinner(value):
    return value


@app.callback(Output("loading-output-1", "children"), [Input('submit-button', 'n_clicks')])
def input_triggers_spinner(value):
    while n is True:
        time.sleep(1)
    return ''


@app.callback([Output('output-div', 'children'),
               Output('output-alert', 'children')],
              [Input('submit-button', 'n_clicks')],
              [State('keyword', 'value'),
               State('nr_videos', 'value')])
def update_output(clicks, keyword, nr_videos):
    if clicks is not None:
        global n

        if not keyword or not nr_videos:
            print("invalid")
            n = False
            return '', failure_alert

        print("Searching for data with keyword " + keyword)

        n = True

        # create crawler and network object
        crawler = YoutubeAPI()
        network = NetworkAnalysis()

        results = crawler.search(keyword, int(nr_videos))
        crawler.process_search_results(results)

        file_name = crawler.create_network(results[0]['_id'])

        # create users network
        network.set_file_name(file_name)
        network.create_network()
        labels = network.getLabels()
        ranks = network.compute_page_rank()
        # network.compute_betweenness_centrality()

        fig = network.display_plotly()

        columns = ['Value', 'Name']
        values = []
        for i in ranks:
            val = {"Value": ranks[i], 'Name': labels[i]}
            values.append(val)

        n = False

        # Create Layout
        return html.Div(
            children=[
                html.Div(id='my-div'),
                dcc.Graph(
                    id='network-graph',
                    figure=fig),
                html.Br(),
                html.Hr(),
                html.Br(),
                create_data_table_network(values, columns)
            ],
            id='dash-container'
        ), success_alert


def create_data_table_network(values, columns):
    """
    Create Dash datatable from Pandas DataFrame.
    :param columns:
    :param labels:
    :param values:
    :return:
    """
    table = dash_table.DataTable(
        id='database-table',
        columns=[{"name": i, "id": i} for i in columns],
        data=values,
        sort_action="native",
        sort_mode='single',
        page_size=20
    )
    return table
