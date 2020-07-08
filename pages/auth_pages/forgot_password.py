import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
from dash.dependencies import Input, Output, State
from sqlalchemy.sql import select

from application.message_logger import MessageLogger
from server import app, engine
from utilities.auth import (
    send_password_key,
    user_table,
    layout_auth
)

success_alert = dbc.Alert(
    'Reset successful. Taking you to change password.',
    color='success',
)
failure_alert = dbc.Alert(
    'Reset unsuccessful. Are you sure that email was correct?',
    color='danger',
)
already_login_alert = dbc.Alert(
    'User already logged in. Taking you to your profile.',
    color='warning'
)

ml = MessageLogger('forgot_password')
logger = ml.get_logger()


@layout_auth('require-nonauthentication')
def layout():
    return dbc.Row(
        dbc.Col(
            [
                html.H3('Forgot Password'),
                dcc.Location(id='forgot-url', refresh=True, pathname='/forgot'),
                dbc.FormGroup(
                    [
                        html.Div(id='forgot-alert'),
                        html.Div(id='forgot-trigger', style=dict(display='none')),
                        html.Br(),

                        dbc.Input(id='forgot-email', autoFocus=True),
                        dbc.FormText('Email'),
                        html.Br(),

                        dbc.Button('Submit email to receive code', id='forgot-button', color='primary'),

                    ]
                )
            ],
            width=4,
            align="center"
        ),
        justify="center"
    )


@app.callback(
    [Output('forgot-alert', 'children'),
     Output('forgot-trigger', 'children')],
    [Input('forgot-button', 'n_clicks')],
    [State('forgot-email', 'value')]
)
def forgot_submit(n_clicks, email):
    if n_clicks > 0:
        logger.info("Verifying if user " + email + " exists")
        table = user_table()
        statement = select([table.c.first]).where(table.c.email == email)
        conn = engine.connect()
        resp = list(conn.execute(statement))
        if len(resp) == 0:
            return failure_alert, no_update
        else:
            firstname = resp[0].first
        conn.close()

        # if it does, send password reset and save info
        if send_password_key(email, firstname, engine):
            logger.info("Changing password for user " + email)
            return success_alert, '/change'
        else:
            logger.info("Cannot change password for user " + email)
            return failure_alert, no_update
    else:
        return failure_alert, no_update


@app.callback(
    Output('forgot-url', 'pathname'),
    [Input('forgot-trigger', 'children')]
)
def forgot_send_to_change(url):
    if url is None or url == '':
        return no_update
    logger.info("Password forgot - changing URL")
    time.sleep(1.5)
    return url
