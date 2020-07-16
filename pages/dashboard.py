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

location = dcc.Location(id='dashboard-url', refresh=True, pathname='/dashboard')
ml = MessageLogger('dashboard')
logger = ml.get_logger()


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

                    # Content Row
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody(
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div("Earnings (Monthly)", className="text-xs font-weight-bold text-primary text-uppercase mb-1"),
                                            html.Div("$40,000", className="h5 mb-0 font-weight-bold text-gray-800")
                                        ], className="mr-2"),
                                        dbc.Col(
                                            html.I(className="fas fa-calendar fa-2x text-gray-300"),
                                            className="col-auto"
                                        )
                                    ],
                                    no_gutters=True,
                                    align="center")
                                )
                            ], className="border-left-primary shadow h-100 py-2"),
                            xl=3,
                            md=6,
                            className="mb-4"
                        )
                    ])

                ], className="container-fluid")
            ],
            style={"margin-top": "40px"}
        )
    )