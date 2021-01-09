import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from flask_login import current_user

from application.message_logger import MessageLogger
from application.network_analysis import NetworkAnalysis
from server import app, engine
from utilities.auth import layout_auth, get_user_searches, get_user_networks, get_user_networks_names, \
    delete_user_network, add_user_search, get_network, update_search_status, update_search_graph
from utilities.utils import create_data_table_network, graph_actions, processing_algorithms, graph_types, \
    create_file_name, NETWORKS_FOLDER


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

failure_graph_alert = dbc.Alert(
    'Cannot change graph type',
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


def algorithm_alert(algorithm):
    return dbc.Alert(
        'Algorithm ' + algorithm + ' is not implemented',
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
                    placeholder="Select action",
                    style={"display": "none"}
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
            id="algo-row-update",
            style={"display": "none"},
        ),

        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='graph-type',
                    options=[{"label": graph, "value": graph_types[graph]} for graph in graph_types],
                    placeholder="Select graph type"
                ),
            ], className="mr-4", xl=5, style={"margin-top": "20px"}),
        ],
            no_gutters=True,
            align="center",
            className="align-items-center",
            id="graph-row-update",
            style={"display": "none"},
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


@app.callback(
    Output('output-statistics-div', 'children'),
    [Input('statistics-trigger', 'children'),
     Input('dash-update-trigger', 'children')]
)
def statistics(set_trigger, update_trigger):
    """
    show statistics
    :param set_trigger:
    :param update_trigger:
    :return:
    """
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


@app.callback(
    Output('output-results-div', 'children'),
    [Input('results-trigger', 'children'),
     Input('dash-update-trigger', 'children')]
)
def update_results(set_trigger, update_trigger):
    """
    show results
    :param set_trigger:
    :param update_trigger:
    :return:
    """
    results = []

    db_results = get_user_networks(current_user.id, engine)

    if len(db_results) == 0:
        return ''

    result_index = 1

    for row in reversed(db_results):
        network_file = row[0]
        data_file = row[1]
        keyword = row[2]
        limit = row[3]
        search_state = row[4]
        algorithm = row[5]
        graph_type= row[6]
        timestamp = row[7]

        if search_state != "Finished":
            # Create Layout
            result_card = dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(
                            html.H6("Results for search:  " + keyword, className="m-0 font-weight-bold text-primary"),
                            lg=4
                        ),
                        dbc.Col(html.Div("Algorithm: " + algorithm), lg=4),
                        dbc.Col(html.Div("Graph: " + graph_type), lg=4)
                    ], style={"width": "100%"})
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

        network = NetworkAnalysis(NETWORKS_FOLDER)
        network.set_files(data_file, network_file)
        network.import_network()
        network.import_ranks()
        nr_nodes = network.get_nr_nodes()

        fig, values, columns = network.create_figure(limit, graph_type)

        # Create Layout
        if nr_nodes > 0:
            result_card = dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H6(str(result_index) + ". Result for search:  " + keyword,
                            className="m-0 font-weight-bold text-primary", id="value_div"), lg=3),
                        dbc.Col(html.Div("Algorithm: " + algorithm), lg=3),
                        dbc.Col(html.Div("Graph: " + graph_type), lg=3),
                        dbc.Col(html.Div("Time: " + str(timestamp)), lg=3)
                    ], style={"width": "100%"})
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
                    dbc.Row([
                        dbc.Col(html.H6(str(result_index) + ". Result for search:  " + keyword,
                            className="m-0 font-weight-bold text-primary", id="value_div"), lg=4),
                        dbc.Col(html.Div("Algorithm: " + algorithm), lg=4),
                        dbc.Col(html.Div("Nodes: " + str(nr_nodes)), lg=4),
                        dbc.Col(html.Div("Time: " + str(timestamp)), lg=4)
                    ], style={"width": "100%"}),
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
     State('algorithm-type', 'value'),
     State('graph-type', 'value')]
)
def edit_network(n_clicks, edit_network, action, nr_users, algorithm, graph):
    """
    Edit the network
    :param n_clicks:
    :param edit_network:
    :param action:
    :param nr_users:
    :param algorithm:
    :param graph:
    :return:
    """
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

            new_network_name = create_file_name()
            old_user_network = get_network(edit_network, engine)
            network = NetworkAnalysis(NETWORKS_FOLDER,)

            network.set_files(edit_network, new_network_name)
            network.import_network()

            if not add_user_search(current_user.id, old_user_network[0][0], new_network_name, edit_network, "Processing Data",
                                   old_user_network[0][5], nr_users, algorithm, old_user_network[0][8], engine):
                return failure_alert, 0

            if network.compute_ranking(algorithm) is False:
                delete_user_network(new_network_name, engine)
                return algorithm_alert(algorithm), 0

            network.store_ranks()

            if not update_search_status(current_user.id, new_network_name, "Finished", engine):
                return failure_alert, 0

        elif action == 'change-graph':
            if graph is None:
                return parameters_alert("graph"), 0

            if not update_search_graph(current_user.id, edit_network, graph, engine):
                return failure_graph_alert, 0

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


@app.callback([Output('action-dropdown', 'style'),
               Output('algo-row-update', 'style'),
               Output('graph-row-update', 'style')],
              [Input('edit-dropdown', 'value'),
               Input('action-dropdown', 'value')])
def update_inputs(edit, action):
    if edit is not None:
        if action == 'change-algorithm':
            return {}, {}, {"display": "none"}
        elif action == 'change-graph':
            return {}, {"display": "none"}, {}
        else:
            return {}, {"display": "none"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "none"}, {"display": "none"}