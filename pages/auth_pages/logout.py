import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
from dash.dependencies import Input, Output
from flask_login import logout_user, current_user

from application.message_logger import MessageLogger
from server import app
from utilities.auth import layout_auth

success_alert = dbc.Alert(
    'Logged out. Taking you to login.',
    color='success',
    dismissable=True,
)
failure_alert = dbc.Alert(
    'Redirecting to login.',
    color='danger',
    dismissable=True,
    duration=5000
)

ml = MessageLogger('logout')
logger = ml.get_logger()


@layout_auth('require-authentication')
def layout():
    return dbc.Row(
        dbc.Col(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("LOGOUT", className="card-title"),
                            dbc.Alert(
                                'Are you sure you want to logout?',
                                color='info',
                                dismissable=True
                            ),
                            dcc.Location(id='logout-url', refresh=True, pathname='/logout'),
                            html.Div(id='logout-hidden-url', style=dict(display='none')),
                            html.Div(id='logout-trigger', style=dict(display='none')),
                            html.Div(id='logout-message'),
                            dbc.Button('Confirm Logout', id='logout-button', color='danger', block=True, size='lg')
                        ]
                    ),
                    style={"width": "20rem", "margin": "0 auto"},
                )
            ],
        ),
    )


@app.callback(
    [Output('logout-trigger', 'children'),
     Output('logout-message', 'children')],
    [Input('logout-button', 'n_clicks')]
)
def logout_card(n_clicks):
    if n_clicks == 0 or n_clicks is None:
        return no_update, no_update
    try:
        logout_user()
        logger.info("User " + current_user.email + " logged out")
        return '/login', success_alert
    except:
        return '/login', failure_alert


@app.callback(
    Output('logout-url', 'pathname'),
    [Input('logout-trigger', 'children')]
)
def logout_wait_and_reload(url):
    if url is None or url == '':
        return no_update
    time.sleep(1)
    return url
