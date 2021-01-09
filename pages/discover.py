import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from flask_login import current_user

from application.message_logger import MessageLogger
from application.network_analysis import NetworkAnalysis
from application.web_crawler import YoutubeAPI
from server import app, engine
from utilities.auth import layout_auth, send_finished_process_confirmation, add_user_search, update_search_status, \
    delete_user_network
from utilities.utils import create_data_table_network, processing_algorithms, graph_types, create_file_name, \
    NETWORKS_FOLDER, COMMENT_PAGES_LIMIT

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


def graph_alert(graph):
    return dbc.Alert(
        'Graph ' + graph + ' is not implemented',
        color='danger',
        dismissable=True
    )


location = dcc.Location(id='discover-url', refresh=True, pathname='/discover')
ml = MessageLogger('discover')
logger = ml.get_logger()


@layout_auth('require-authentication')
def layout():
    # if current_user.is_authenticated:
    text_card = dbc.Card([
        dbc.CardHeader([
            html.H6("Discover Influencers on YouTube", className="m-0 font-weight-bold text-primary"),
        ],
            className="py-3 d-flex flex-row align-items-center justify-content-between"),
        dbc.CardBody(
            [
                html.Div(id='home-login-trigger', style=dict(display='none')),
                html.H5('What the application does: '),
                html.Ul(
                    [
                        html.Li("Searches the YouTube platform for videos regarding the search keyword"),
                        html.Li("Downloads the necessary data from videos (title, description, comments and others)"),
                        html.Li("Creates a graph by using the user connections that commented on the videos"),
                        html.Li("Determines the most influential users using the selected algorithm"),
                        html.Li("Displays the created graph and the results from processing algorithm"),
                        html.Li("All the results can all be seen in the DASHBOARD page")
                    ]
                ),
                html.Br(),
                html.H5('To use the application, enter the options and click Search!'),
            ]
        )],
        className="shadow mb-4"
    )

    search_card = dbc.Card([
        dbc.CardHeader([
            html.H6("Search", className="m-0 font-weight-bold text-primary"),
        ],
            className="py-3 d-flex flex-row align-items-center justify-content-between"),
        dbc.CardBody(
            [
                html.Div(id='output-alert'),
                html.H5("Keywords: "),
                dcc.Input(id='keyword', value='', type='text', placeholder="type the keywords"),
                html.Br(), html.Br(),
                html.H5("Number of videos analyzed:"), html.Div(id="range-val-videos"),
                dcc.Input(id='nr_videos', value='1', type='range', placeholder="Valid from 1 to 10", min=1,
                          max=10,
                          step=1),
                html.Br(),
                html.H5("Number of influencers found:"), html.Div(id="range-val-users"),
                dcc.Input(id='nr_users', value='30', type='range', placeholder="Valid from 1 to 100", min=1,
                          max=100,
                          step=1),
                html.Br(),
                html.H5("Graph type: "),
                dcc.Dropdown(
                    id='graph_type',
                    options=[{"label": graph, "value": graph_types[graph]}
                             for graph in graph_types],
                    placeholder="Select graph type"
                ),
                html.Br(),
                html.H5("Processing Algorithm: "),
                dcc.Dropdown(
                    id='algorithm_type',
                    options=[{"label": algo, "value": processing_algorithms[algo]}
                             for algo in processing_algorithms],
                    placeholder="Select algorithm"
                ),
                html.Br(),
                dbc.Button('Search', color='primary', id='submit-button'),
            ]
        )],
        className="shadow mb-4"
    )

    result_card = dbc.Card([
        dbc.CardHeader([
            html.H6("Results", className="m-0 font-weight-bold text-primary"),
        ],
            className="py-3 d-flex flex-row align-items-center justify-content-between"),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-1",
                    children=html.Div(id="loading-output-1"),
                    type="circle",
                ),
                html.Div(id='output-div', style={"width": "100%"}),
            ],
        )],
        className="shadow mb-4",
        id="result-card-id",
        style={"visibility": "hidden"}
    )

    return dbc.Row(
        dbc.Col(
            children=[
                location,
                dbc.Container([
                    # Heading
                    html.Div(
                        html.H1("Discover", className="h3 mb-0 text-gray-800"),
                        className="d-sm-flex align-items-center justify-content-between mb-4"
                    ),

                    # Search
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.CardDeck(
                                    [
                                        search_card,
                                        text_card
                                    ]
                                ),
                                width=12
                            ),
                            dbc.Col(result_card, width=12),
                        ],
                        className="mb-4",
                    ),

                    ],
                    style={"margin-top": "40px"},
                ),
            ]
        ),
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
               State('graph_type', 'value'),
               State('algorithm_type', 'value')])
def update_results(clicks, keyword, nr_videos, nr_users, graph_type, algorithm):
    if clicks is not None:
        if not keyword or not nr_videos or not nr_users or not graph_type or not algorithm:
            logger.error("Invalid user input data")
            return '', failure_alert, ''

        if current_user.is_authenticated:
            logger.info("User " + str(current_user.first) + " " + str(current_user.last) + " authenticated")
        else:
            logger.warning("User not authenticated")

        limit = int(nr_users)

        # create crawler and network object
        file_name = create_file_name()
        crawler = YoutubeAPI(file_name, NETWORKS_FOLDER, COMMENT_PAGES_LIMIT)
        network = NetworkAnalysis(NETWORKS_FOLDER)

        if not add_user_search(current_user.id, keyword, file_name, file_name, "Retrieving Data", nr_videos, limit,
                               algorithm, graph_type, engine):
            if not update_search_status(current_user.id, file_name, "Retrieving Data", engine):
                return '', failure_alert, ''

        results = crawler.search(keyword, int(nr_videos))
        crawler.process_search_results(results)

        try:
            network_data = results[0]['_id']
            if not crawler.create_network(network_data):
                logger.error("Cannot create network: " + file_name)
        except TypeError:
            return '', quota_exceeded_alert, ''

        if not update_search_status(current_user.id, file_name, "Processing Data", engine):
            return '', failure_alert, ''

        # create users network
        network.set_files(file_name, file_name)
        network.create_network()

        if not network.compute_ranking(algorithm):
            delete_user_network(file_name, engine)
            return '', graph_alert(algorithm), ''

        network.store_network()

        fig, values, columns = network.create_figure(limit, graph_type)

        if send_finished_process_confirmation(current_user.email, current_user.first, keyword):
            logger.info("Confirmation sent to " + str(current_user.email) + " " + str(current_user.first))
        else:
            logger.warning("Confirmation NOT sent to " + str(current_user.email) + " " + str(current_user.first))

        if not update_search_status(current_user.id, file_name, "Finished", engine):
            return '', failure_alert, ''

        # Create Layout
        return html.Div(
            children=[
                html.Div(id='my-div'),
                html.Br(),
                html.H5("Users Graph"),
                dcc.Graph(
                    id='network-graph',
                    figure=fig,
                    responsive=True),
                html.Br(),
                html.Hr(),
                html.Br(),
                html.H5("Users Table"),
                html.Br(),
                create_data_table_network(values, columns)
            ],
            id='dash-container'
        ), success_alert, ''
    else:
        return '', '', ''


@app.callback(Output('result-card-id', 'style'),
              [Input('submit-button', 'n_clicks')])
def results_visibility(clicks):
    if clicks is not None:
        if clicks == 1:
            return {"visibility": "visible"}
        else:
            return {}
    else:
        return {"visibility": "hidden"}


