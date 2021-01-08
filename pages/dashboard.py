import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from flask_login import current_user

from application.message_logger import MessageLogger
from application.network_analysis import NetworkAnalysis
from application.web_crawler import YoutubeAPI
from server import app, engine
from utilities.auth import layout_auth, get_user_searches, get_user_networks, get_user_networks_names, \
    delete_user_network, add_user_search, get_network, update_user_search
from utilities.utils import create_data_table_network, graph_actions, processing_algorithms


def success_alert(message, action):
    return dbc.Alert(
        message + " " + action + ' is successful',
        color='success',
        dismissable=True
    )


failure_alert = dbc.Alert(
    'Cannot add graph network',
    color='danger',
    dismissable=True
)


def parameters_alert(message):
    return dbc.Alert(
        'No ' + message + ' selected',
        color='danger',
        dismissable=True,
        duration=5000
    )


def graph_alert(graph):
    return dbc.Alert(
        'Graph ' + graph + ' is not implemented',
        color='danger',
        dismissable=True
    )


location = dcc.Location(id='dashboard-url', refresh=True, pathname='/dashboard')
ml = MessageLogger('dashboard')
logger = ml.get_logger()


def display_data(title, text, data_type, image):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Div(title, className="text-xs font-weight-bold text-primary text-uppercase mb-1"),
                        html.Div(text, className="h5 mb-0 font-weight-bold text-gray-800")
                    ], className="mr-2"),
                    dbc.Col(
                        html.I(className="fas fa-" + image + " fa-2x text-gray-300"),
                        className="col-auto"
                    )
                ],
                    no_gutters=True,
                    align="center")
            )
        ],
        className="border-left-" + data_type + " shadow h-100 py-2"),
        xl=3,
        md=4,
        className="mb-4"
    )


def display_action_button():
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div("Run query", className="text-xs font-weight-bold text-primary text-uppercase mb-1"),
                    ], className="mr-2"),
                ],
                    no_gutters=True,
                    align="center"
                ),

                dbc.Row([
                    dbc.Col([
                        html.Br(),
                        dbc.Button(
                            html.I(className="fas fa-play fa-2x text-gray-300"),
                            color="light",
                            id="action-button",
                            className="mr-1"
                        ),
                    ], className="col-auto"
                    ),
                ],
                    no_gutters=True,
                    align="center"),
            ])
        ], className="border-left-danger shadow h-100 py-2"),
        xl=3,
        md=4,
        className="mb-4"
    )


def collapse(data):
    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(
                    html.H6(
                        dbc.Button(
                            [html.I(className="fas fa-edit text-gray-300"), " Edit Searches", ],
                            color="link",
                            id="collapse-button",
                        ),
                        className="m-0 font-weight-bold text-primary"
                    ),
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        data,
                    ),
                    id="collapse",
                ),
            ],
            className="border-left-danger shadow"
        ),
        xl=12,
        md=4,
        className="mb-4"
    )


def display_networks(networks, keywords):
    return [
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="edit-dropdown",
                    options=[{'label': str(networks.index(j) + 1) + ". " + str(i), 'value': j}
                             for (i, j) in zip(keywords, networks)],
                    placeholder="Select graph"
                ),
            ], className="mr-4", xl=5, style={"margin-top": "20px"}),
            dbc.Col([
                dcc.Dropdown(
                    id="action-dropdown",
                    options=[{"label": graph, "value": graph_actions[graph]}
                             for graph in graph_actions],
                    placeholder="Select action"
                ),
            ], className="mr-4", xl=5, style={"margin-top": "20px"}),
        ],
            no_gutters=True,
            align="center",
            className="align-items-center",
        ),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='algorithm-type',
                    options=[{"label": algo, "value": processing_algorithms[algo]}
                             for algo in processing_algorithms],
                    placeholder="Select algorithm"
                ),
            ], className="mr-4", xl=5, style={"margin-top": "20px"}),
            dbc.Col([
                dbc.Row([
                    dbc.Col(
                        dcc.Input(id='nr-users', value='30', type='range', placeholder="Valid from 1 to 100",
                                  min=1, max=100, step=1, style={"margin-top": "20px"}),
                    ),
                    dbc.Col(
                        html.Div(id="range-val", style={"margin-top": "20px"}),
                    ),
                ])
            ], className="mr-4", xl=5),
        ],
            no_gutters=True,
            align="center",
            className="align-items-center",
        ),

        dbc.Row([
            dbc.Col([
                dbc.Button(
                    html.I(className="fas fa-play fa-2x text-gray-300"),
                    color="light",
                    id="action-button",
                    className="mr-2"
                ),
            ], className="mr-4", xl=5),
        ],
            no_gutters=True,
            align="center",
            className="align-items-center",
            style={"margin-top": "20px"}
        )
    ]


@layout_auth('require-authentication')
def layout():
    return dbc.Row(
        dbc.Col(
            children=[
                dbc.Container([
                    location,

                    # Heading
                    html.Div(
                        html.H1("Dashboard", className="h3 mb-0 text-gray-800"),
                        className="d-sm-flex align-items-center justify-content-between mb-4"
                    ),

                    # Statistics
                    html.Div(1, id='statistics-trigger', style=dict(display='none')),
                    html.Div(id='output-statistics-div', style={"width": "100%"}),
                    html.Div(0, id='dash-update-trigger', style=dict(display='none')),
                    html.Div(0, id='redirect-dash-trigger', style=dict(display='none')),

                    html.Div(id='delete-trigger'),

                    # Search results
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.CardDeck(
                                    [
                                        html.Div(1, id='results-trigger', style=dict(display='none')),
                                        html.Div(id='output-results-div', style={"width": "100%"}),
                                    ]
                                ),
                                width=12
                            ),
                        ],
                        className="mb-4",
                    ),

                ], className="container-fluid")
            ],
            style={"margin-top": "40px"}
        )
    )


# function to show statistics
@app.callback(
    Output('output-statistics-div', 'children'),
    [Input('statistics-trigger', 'children'),
     Input('dash-update-trigger', 'children')]
)
def statistics(set_trigger, update_trigger):
    nr_videos = 0
    nr_influencers = 0

    results = get_user_searches(current_user.id, engine)

    nr_searches = len(results)
    if nr_searches == 0:
        search_status = "No results"
    else:
        search_status = results[nr_searches - 1][0]
        for row in results:
            nr_videos += row[1]
            nr_influencers += row[2]

    networks, keywords = get_user_networks_names(current_user.id, engine)

    return dbc.Row([
        display_data("Nr. of searches", str(nr_searches), "primary", "calendar"),
        display_data("Nr. of analyzed videos", str(nr_videos), "info", "video"),
        display_data("Nr. of influencers", str(nr_influencers), "warning", "user"),
        display_data("Latest search", search_status, "success", "spinner"),
        collapse(display_networks(networks, keywords)),
    ])


# function to show results
@app.callback(
    Output('output-results-div', 'children'),
    [Input('results-trigger', 'children'),
     Input('dash-update-trigger', 'children')]
)
def profile_values(set_trigger, update_trigger):
    results = []
    graph_type = "3"

    db_results = get_user_networks(current_user.id, engine)

    if len(db_results) == 0:
        return ''

    result_index = 1

    for row in reversed(db_results):
        file_name = row[0]
        keyword = row[1]
        limit = row[2]
        search_state = row[3]
        algorithm = row[4]
        timestamp = row[5]

        if search_state != "Finished":
            # Create Layout
            result_card = dbc.Card([
                dbc.CardHeader([
                    html.H6("Results for search:  " + keyword, className="m-0 font-weight-bold text-primary"),
                    html.Div("Algorithm: " + algorithm),
                ],
                    className="py-3 d-flex flex-row align-items-center justify-content-between"),
                dbc.CardBody(
                    [
                        html.Div(
                            children=[
                                html.Div(id='my-div'),
                                html.Br(),
                                html.H5(search_state),
                                html.Br(),
                            ],
                            id='dash-container'
                        )
                    ],
                )],
                className="shadow mb-4"
            )
            results.append(result_card)

            continue

        network = NetworkAnalysis()
        network.set_file_name(file_name)
        network.import_network()
        nr_nodes = network.get_nr_nodes()

        fig, values, columns = network.create_figure(limit, graph_type)

        # Create Layout
        if nr_nodes > 0:
            result_card = dbc.Card([
                dbc.CardHeader([
                    html.H6(str(result_index) + ". Result for search:  " + keyword,
                            className="m-0 font-weight-bold text-primary", id="value_div"),
                    html.Div("Algorithm: " + algorithm),
                    html.Div(timestamp)
                    ],
                    className="py-3 d-flex flex-row align-items-center justify-content-between"
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            children=[
                                html.Div(id='my-div'),
                                html.Br(),
                                html.H5("Users Graph"),
                                dcc.Graph(
                                    id='network-graph-2',
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
                        )
                    ],
                )],
                className="shadow mb-4"
            )
        else:
            result_card = dbc.Card([
                dbc.CardHeader([
                    html.H6(str(result_index) + ". Result for search:  " + keyword,
                            className="m-0 font-weight-bold text-primary", id="value_div"),
                    html.Div("Algorithm: " + algorithm),
                    html.Div("Nodes: " + str(nr_nodes)),
                    html.Div(timestamp)
                ],
                    className="py-3 d-flex flex-row align-items-center justify-content-between"),
                dbc.CardBody(
                    [],
                )],
                className="shadow mb-4"
            )

        result_index = result_index + 1
        results.append(result_card)

    return results


@app.callback(
    [Output('delete-trigger', 'children'),
     Output('dash-update-trigger', 'children')],
    [Input('action-button', 'n_clicks')],
    [State('edit-dropdown', 'value'),
     State('action-dropdown', 'value'),
     State('nr-users', 'value'),
     State('algorithm-type', 'value')]
)
def profile_values(n_clicks, edit_network, action, nr_users, algorithm):
    if n_clicks is not None and n_clicks > 0:
        if edit_network is None:
            return parameters_alert("network"), 0
        if action is None:
            return parameters_alert("action"), 0
        elif action == 'delete':
            delete_user_network(edit_network, engine)
        elif action == 'change-algorithm':
            if nr_users is None:
                return parameters_alert("nr users"), 0
            if algorithm is None:
                return parameters_alert("algorithm"), 0

            crawler = YoutubeAPI()
            network = NetworkAnalysis()
            network.set_file_name(edit_network)
            network.import_network()

            file_name = crawler.get_file_name()
            old_user_network = get_network(edit_network, engine)

            if not add_user_search(current_user.id, old_user_network[0][0], file_name, "Processing Data",
                                   old_user_network[0][4], nr_users, algorithm, engine):
                return failure_alert, 0

            if algorithm == "page-rank":
                network.compute_page_rank()
            elif algorithm == "betweenness-centrality":
                network.compute_betweenness_centrality()
            elif algorithm == "vote-rank":
                network.compute_vote_rank()
            else:
                delete_user_network(file_name, engine)
                return graph_alert(algorithm), 0

            network.set_file_name(file_name)
            network.store_network()
            network.store_labels()

            if not update_user_search(current_user.id, file_name, "Finished", engine):
                return failure_alert, 0

        return success_alert(edit_network, action), 1


@app.callback(Output("range-val", "children"),
              [Input('nr-users', 'value')])
def input_triggers_spinner(value):
    return value


@app.callback(
    Output('redirect-dash-trigger', 'children'),
    [Input('dash-update-trigger', 'children')]
)
def register_success(value):
    if value is not None and value == 1:
        time.sleep(2)
        return dcc.Location(pathname='/dashboard', id="redirect", refresh=True)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
