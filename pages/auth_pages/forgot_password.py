import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
from dash.dependencies import Input, Output, State
from sqlalchemy.sql import select

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
def forgot_submit(submit, email):
    # get first name
    print('getting first name')
    table = user_table()
    statement = select([table.c.first]). \
        where(table.c.email == email)
    conn = engine.connect()
    resp = list(conn.execute(statement))
    resp[0].first
    if len(resp) == 0:
        return failure_alert, no_update
    else:
        firstname = resp[0].first
    conn.close()

    # if it does, send password reset and save info
    if send_password_key(email, firstname, engine):
        return success_alert, '/change'
    else:
        return failure_alert, no_update


@app.callback(
    Output('forgot-url', 'pathname'),
    [Input('forgot-trigger', 'children')]
)
def forgot_send_to_change(url):
    print(url)
    if url is None or url == '':
        return no_update
    print('FORGOT - CHANGING URL')
    time.sleep(1.5)
    return url
