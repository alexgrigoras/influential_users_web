import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from flask_login import current_user

from application.message_logger import MessageLogger
from application.network_analysis import NetworkAnalysis
from server import app, engine
from utilities.auth import layout_auth, get_user_searches, get_user_networks, get_user_networks_names, \
    delete_user_network
from utilities.utils import create_data_table_network


def success_alert(message, action):
    return dbc.Alert(
        message + " " + action + ' successfully',
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

no_action_alert = dbc.Alert(
    'No action selected',
    color='danger',
    dismissable=True,
    duration=5000
)

no_network_alert = dbc.Alert(
    'No network selected',
    color='danger',
    dismissable=True,
    duration=5000
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
        ], className="border-left-" + data_type + " shadow h-100 py-2"),
        xl=3,
        md=6,
        className="mb-4"
    )


action_button = dbc.Col(
    dbc.Button(
        html.I(className="fas fa-play fa-2x text-gray-300"),
        color="light",
        id="action-button",
        className="mr-1"
    ),
    className="col-auto"
)


def display_networks(title, networks, data_type, dropdown_id, action):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Div(title, className="text-xs font-weight-bold text-primary text-uppercase mb-1"),
                        dcc.Dropdown(
                            id=dropdown_id,
                            options=[{'label': i, 'value': i} for i in networks],
                        ),
                    ], className="mr-2"),
                    action
                ],
                    no_gutters=True,
                    align="center")
            )
        ], className="border-left-" + data_type + " shadow h-100 py-2"),
        xl=3,
        md=6,
        className="mb-4"
    )


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


# function to show profile values
@app.callback(
    Output('output-statistics-div', 'children'),
    [Input('statistics-trigger', 'children')]
)
def profile_values(trigger):
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

    networks = get_user_networks_names(current_user.id, engine)
    graph_actions = ["delete", "update"]

    return dbc.Row([
        display_data("Nr. of searches", str(nr_searches), "primary", "calendar"),
        display_data("Most used algorithm", search_status, "warning", "code"),
        display_data("Nr. of analyzed videos", str(nr_videos), "info", "video"),
        display_data("Nr. of influencers", str(nr_influencers), "warning", "user"),
        display_data("Latest search", search_status, "success", "spinner"),
        display_networks("Edit graph", networks, "danger", "edit-dropdown", None),
        display_networks("Action for graph", graph_actions, "dark", "action-dropdown", action_button),
    ])


# function to show results
@app.callback(
    Output('output-results-div', 'children'),
    [Input('results-trigger', 'children')]
)
def profile_values(trigger):
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
                    className="py-3 d-flex flex-row align-items-center justify-content-between"),
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
    Output('delete-trigger', 'children'),
    [Input('action-button', 'n_clicks')],
    [State('edit-dropdown', 'value'),
     State('action-dropdown', 'value')]
)
def profile_values(n_clicks, edit, action):
    if n_clicks is not None and n_clicks > 0:
        if edit is None:
            return no_network_alert
        if action is None:
            return no_action_alert
        elif action == 'delete':
            delete_user_network(edit, engine)

        return success_alert(edit, action)
