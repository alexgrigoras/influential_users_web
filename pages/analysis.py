import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input, State
from flask_login import current_user

from application.message_logger import MessageLogger
from application.network_analysis import NetworkAnalysis
from application.youtube_api import YoutubeAPI
from server import app
from utilities.auth import layout_auth, send_finished_process_confirmation

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

quota_exceeded_alert = dbc.Alert(
    'Data retrieval from YouTube is limited! Try the next day.',
    color='danger',
    dismissable=True
)

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='analysis-url', refresh=True, pathname='/analysis')
ml = MessageLogger('analysis')
logger = ml.get_logger()


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
                html.H6('[DISCLAIMER] The application loses its state if the page is reloaded or closed!'),
                html.Br(),
                html.H5('To use the application, enter the options below and click SEARCH'),
                html.Div(id='output-alert'),
                html.H5("Keyword: "),
                dcc.Input(id='keyword', value='', type='text', placeholder="keyword"),
                html.Br(), html.Br(),
                html.H5("Number of videos: "), html.Div(id="range-val-videos"),
                dcc.Input(id='nr_videos', value='1', type='range', placeholder="Valid from 1 to 10", min=1, max=10,
                          step=1),
                html.H5("Number of users: "), html.Div(id="range-val-users"),
                dcc.Input(id='nr_users', value='30', type='range', placeholder="Valid from 1 to 100", min=1, max=100,
                          step=1),
                html.H5("Graph type: "),
                dcc.RadioItems(
                    id="graph_type",
                    options=[
                        {'label': "3D Spring", 'value': '3'},
                        {'label': "2D Graph", 'value': '2'}
                    ],
                    value='3',
                    labelStyle={'display': 'inline-block', "margin-right": "15px"}
                ),
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


@app.callback(Output("range-val-videos", "children"),
              [Input('nr_videos', 'value')])
def input_triggers_spinner(value):
    return value


@app.callback(Output("range-val-users", "children"),
              [Input('nr_users', 'value')])
def input_triggers_spinner(value):
    return value


@app.callback([Output('output-div', 'children'),
               Output('output-alert', 'children'),
               Output("loading-output-1", "children")],
              [Input('submit-button', 'n_clicks')],
              [State('keyword', 'value'),
               State('nr_videos', 'value'),
               State('nr_users', 'value'),
               State('graph_type', 'value')])
def update_output(clicks, keyword, nr_videos, nr_users, graph_type):
    if clicks is not None:
        if not keyword or not nr_videos or not nr_users or not graph_type:
            logger.error("Invalid user input data")
            return '', failure_alert, ''

        if current_user.is_authenticated:
            logger.info("User " + current_user.first + " " + current_user.last + " authenticated")
        else:
            logger.warning("User not authenticated")

        limit = int(nr_users)

        # create crawler and network object
        crawler = YoutubeAPI()
        network = NetworkAnalysis()

        results = crawler.search(keyword, int(nr_videos))
        crawler.process_search_results(results)

        try:
            network_data = results[0]['_id']
            file_name = crawler.create_network(network_data)
        except TypeError:
            return '', quota_exceeded_alert, ''

        # create users network
        network.set_file_name(file_name)
        network.create_network()
        labels = network.get_labels()
        ranks = network.compute_page_rank()
        # network.compute_betweenness_centrality()

        columns = ['Value', 'Name']
        values = []
        index = 0
        selected_nodes = []
        for u_id in sorted(ranks, key=ranks.get, reverse=True):
            selected_nodes.append(u_id)
            val = {"Value": check_value(ranks, u_id), 'Name': check_value(labels, u_id)}
            values.append(val)
            index += 1
            if index >= limit:
                break

        fig = network.display_plotly(selected_nodes, graph_type)

        if send_finished_process_confirmation(current_user.email, current_user.first, keyword):
            logger.info("Confirmation sent to " + current_user.email + " " + current_user.first)
        else:
            logger.warning("Confirmation NOT sent to " + current_user.email + " " + current_user.first)

        # Create Layout
        return html.Div(
            children=[
                html.Div(id='my-div'),
                html.Br(),
                html.H5("Users Graph"),
                dcc.Graph(
                    id='network-graph',
                    figure=fig),
                html.Br(),
                html.Hr(),
                html.Br(),
                html.H5("Users Table"),
                html.Br(),
                create_data_table_network(values, columns)
            ],
            id='dash-container'
        ), success_alert, ''


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


def check_value(array, value):
    if value in array:
        return array[value]
    else:
        return "x"
