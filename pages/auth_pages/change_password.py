import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
from dash.dependencies import Input, Output, State

from application.message_logger import MessageLogger
from server import app, engine
from utilities.auth import (
    validate_password_key,
    change_password,
    layout_auth
)

success_alert = dbc.Alert(
    'Reset successful. Redirecting to login!',
    color='success',
)
failure_alert = dbc.Alert(
    'Reset unsuccessful. Are you sure the email and code were correct?',
    color='danger',
)
already_login_alert = dbc.Alert(
    'User already logged in. Redirecting your profile.',
    color='warning'
)

ml = MessageLogger('change_password')
logger = ml.get_logger()


@layout_auth('require-nonauthentication')
def layout():
    return dbc.Row(
        dbc.Col(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4("Change Password", className="card-title"),

                            dcc.Location(id='change-url', refresh=True, pathname='/change'),
                            html.Div(id='change-trigger', style=dict(display='none')),
                            dbc.FormGroup(
                                [
                                    html.Div(id='change-alert'),
                                    html.Br(),

                                    dbc.Input(id='change-email', autoFocus=True),
                                    dbc.FormText('Email'),
                                    html.Br(),

                                    dbc.Input(id='change-key', type='password'),
                                    dbc.FormText('Code'),
                                    html.Br(),

                                    dbc.Input(id='change-password', type='password'),
                                    dbc.FormText('New password'),
                                    html.Br(),

                                    dbc.Input(id='change-confirm', type='password'),
                                    dbc.FormText('Confirm new password'),
                                    html.Br(),

                                    dbc.Button('Submit password change', id='change-button', color='primary'),

                                ]
                            )
                        ]
                    ),
                    style={"width": "20rem", "margin": "0 auto"},
                )
            ],
        ),
    )


# function to validate inputs
@app.callback(
    [Output('change-password', 'valid'),
     Output('change-password', 'invalid'),
     Output('change-confirm', 'valid'),
     Output('change-confirm', 'invalid'),
     Output('change-button', 'disabled')],
    [Input('change-password', 'value'),
     Input('change-confirm', 'value')]
)
def change_validate_inputs(password, confirm):
    password_valid = False
    password_invalid = False
    confirm_valid = False
    confirm_invalid = True
    disabled = True

    bad = [None, '']

    if password in bad:
        pass
    elif isinstance(password, str):
        password_valid = True
        password_invalid = False

    if confirm in bad:
        pass
    elif confirm == password:
        confirm_valid = True
        confirm_invalid = False

    if password_valid and confirm_valid:
        disabled = False

    return (
        password_valid,
        password_invalid,
        confirm_valid,
        confirm_invalid,
        disabled
    )


@app.callback(
    [Output('change-alert', 'children'),
     Output('change-trigger', 'children')],
    [Input('change-button', 'n_clicks')],
    [State('change-email', 'value'),
     State('change-key', 'value'),
     State('change-password', 'value'),
     State('change-confirm', 'value')]
)
def submit_change(submit, email, key, password, confirm):
    # all inputs have been previously validated
    # validate_password_key(email,key,engine)
    if validate_password_key(email, key, engine):
        logger.info('Validate password success')
        # if that returns true, update the user information
        if change_password(email, password, engine):
            return success_alert, '/login'
        else:
            logger.error('Validate password failed after change user')
            pass
    else:
        logger.error('Validate password failed')
        pass
    return failure_alert, no_update


@app.callback(
    Output('change-url', 'pathname'),
    [Input('change-trigger', 'children')]
)
def change_send_to_login(url):
    if url is None or url == '':
        return no_update
    logger.info('Redirecting to profile')
    time.sleep(1.5)
    return url
