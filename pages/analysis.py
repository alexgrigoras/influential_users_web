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
        [
            dbc.Col(
                children=[
                    location,
                    html.Div(id='home-login-trigger', style=dict(display='none')),

                    html.H3('Search'),
                    html.Br(),

                    html.H5("Keyword: "),
                    dcc.Input(id='keyword', value='', type='text'),
                    html.Br(), html.Br(),
                    html.H5("Nr videos: "),
                    dcc.Input(id='nr_videos', value='', type='number'),
                    html.Br(), html.Br(),
                    dbc.Button('Search', color='primary', id='submit-button'),
                    html.Br(), html.Br(),
                    dcc.Loading(
                        id="loading-1",
                        type="graph",
                        children=html.Div(id="loading-output-1")
                    )
                ],
                width=3
            ),
            dbc.Col(html.Div(id='output-div'))
        ]
    )


@app.callback(Output("loading-output-1", "children"), [Input('submit-button', 'n_clicks')])
def input_triggers_spinner(value):
    while n is True:
        time.sleep(1)
    return ''


@app.callback(Output('output-div', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('keyword', 'value'),
               State('nr_videos', 'value')])
def update_output(clicks, keyword, nr_videos):
    if clicks is not None:
        print("Searching for data with keyword " + keyword)

        global n

        n = True

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

        # network.display_tree()
        # network.display_graphviz()
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
                create_data_table_network(values, columns)
            ],
            id='dash-container'
        )


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
