import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import no_update

from flask_login import login_user, current_user
from werkzeug.security import check_password_hash

from application.message_logger import MessageLogger
from server import app, User
from utilities.auth import layout_auth

success_alert = dbc.Alert(
    'Logged in successfully. Taking you home!',
    color='success',
    dismissable=True
)
failure_alert = dbc.Alert(
    'Login unsuccessful. Try again.',
    color='danger',
    dismissable=True,
    duration=5000
)
already_login_alert = dbc.Alert(
    'User already logged in. Taking you home!',
    color='warning',
    dismissable=True,
    duration=5000
)

ml = MessageLogger('login')
logger = ml.get_logger()


@layout_auth('require-nonauthentication')
def layout():
    return dbc.Row(
        dbc.Col(
            children=[
                dbc.Card([
                    dbc.CardBody(
                        [
                            dcc.Location(id='login-url', refresh=True, pathname='/login'),

                            html.H4("LOGIN", className="card-title"),

                            html.Div(id='login-trigger', style=dict(display='none')),
                            html.Div(id='login-alert'),

                            dbc.FormGroup(
                                [
                                    dbc.Alert(
                                        'You need to authenticate to use the application!',
                                        color='info',
                                        dismissable=True
                                    ),
                                    dbc.Input(id='login-email', autoFocus=True),
                                    dbc.FormText('Email'),

                                    html.Br(),
                                    dbc.Input(id='login-password', type='password'),
                                    dbc.FormText('Password'),

                                    html.Br(),
                                    dbc.Button('Log In', color='primary', id='login-button', block=True, size='lg'),

                                    html.Hr(),
                                    dbc.FormText("Don't have an account yet? "), dbc.FormText(dcc.Link("Sign Up!", href='/register')),
                                    html.Hr(),
                                    dbc.FormText("Having issues logging in? "), dbc.FormText(dcc.Link("Reset Password!", href='/forgot'))
                                ]
                            )
                        ]
                    )],
                    className="mx-auto border-0 bg-light",
                    style={"margin-top": "40px", "margin-bottom": "40px"},
                )
            ],
            lg=3,
            align="center"
        ),
        justify="center"
    )


@app.callback(
    [Output('login-trigger', 'children'),
     Output('login-alert', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('login-email', 'value'),
     State('login-password', 'value')]
)
def login_success(n_clicks, email, password):
    """
    logs in the user
    """
    if n_clicks is not None:
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                if email:
                    logger.info("User " + email + " logged in")
                return '/dashboard', success_alert
            else:
                if email:
                    logger.error("User " + email + " failed to log in")
                return no_update, failure_alert
        else:
            if email:
                logger.error("User " + email + " failed to log in")
            return no_update, failure_alert
    else:
        if email:
            logger.error("User " + email + " failed to log in")
        return no_update, ''


@app.callback(
    Output('login-url', 'pathname'),
    [Input('login-trigger', 'children')]
)
def login_wait_and_reload(url):
    if url is None or url == '':
        return no_update
    return url
