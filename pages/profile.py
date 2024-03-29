import time

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
from dash.dependencies import Input, Output, State
from flask_login import current_user

from application.message_logger import MessageLogger
from server import app, engine
from utilities.auth import change_user, change_password, layout_auth, del_user, send_delete_confirmation, \
    send_profile_change

success_alert = dbc.Alert(
    'Changes saved successfully.',
    color='success',
)
failure_alert = dbc.Alert(
    'Unable to save changes.',
    color='danger',
)
login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='warning',
)
success_delete = dbc.Alert(
    'Account deleted successfully.',
    color='success',
)
failure_delete = dbc.Alert(
    'Account cannot be deleted',
    color='danger',
)

ml = MessageLogger('analysis')
logger = ml.get_logger()


@layout_auth('require-authentication')
def layout():
    return dbc.Row(
        dbc.Col(
            children=[
                dcc.Location(id='profile-url', refresh=True, pathname='/profile'),
                dbc.Card([
                    dbc.CardBody(
                        [
                            html.H4("Profile", className="card-title"),
                            html.Div(1, id='profile-trigger', style=dict(display='none')),
                            html.Div(1, id='redirect-trigger', style=dict(display='none')),

                            html.Div(id='profile-alert'),
                            html.Div(id='profile-alert-login'),
                            html.Div(id='profile-alert-delete'),
                            html.Div(id='profile-delete-trigger', style=dict(display='none')),
                            html.Div(id='profile-login-trigger', style=dict(display='none')),
                            html.Br(),

                            dbc.FormGroup(
                                [
                                    # First, first input, and formtext
                                    dbc.Label('First:', id='profile-first'),
                                    dbc.Input(placeholder='Change first name...', id='profile-first-input'),
                                    dbc.FormText(id='profile-first-formtext', color='secondary'),
                                    html.Br(),

                                    # last, last input, and formtext
                                    dbc.Label('Last:', id='profile-last'),
                                    dbc.Input(placeholder='Change last name...', id='profile-last-input'),
                                    dbc.FormText(id='profile-last-formtext', color='secondary'),
                                    html.Br(),

                                    # email, formtext
                                    dbc.Label('Email:', id='profile-email'),

                                    html.Hr(),

                                    # password, input, confirm input
                                    dbc.Label('Change password', id='profile-password'),
                                    html.Br(),
                                    dbc.Input(placeholder='Change password...', id='profile-password-input',
                                              type='password'),
                                    dbc.FormText('Change password', color='secondary',
                                                 id='profile-password-input-formtext'),
                                    html.Br(),
                                    dbc.Input(placeholder='Confirm password...', id='profile-password-confirm',
                                              type='password'),
                                    dbc.FormText('Confirm password', color='secondary',
                                                 id='profile-password-confirm-formtext'),
                                    html.Br(),

                                    dbc.Button('Save changes', color='pri'
                                                                     ''
                                                                     'mary', id='profile-submit', disabled=True,
                                               block=True, size='lg'),

                                    html.Br(),
                                    html.Hr(),

                                    dbc.Label("Don't use this account anymore?", id='primary'),
                                    html.Br(),
                                    dbc.Button('Delete account', color='secondary', id='profile-delete', block=True,
                                               size='lg'),
                                ]
                            ),
                        ]
                    )],
                    className="mx-auto border-0 bg-light",
                    style={"margin": "40px auto 40px auto"},
                ),
            ],
            lg=3,
            align="center",
        ),
        justify="center"
    )


# function to show profile values
@app.callback(
    [Output('profile-alert-login', 'children'),
     Output('profile-login-trigger', 'children')] + \
    [Output('profile-' + x, 'children') for x in ['first', 'last', 'email']] + \
    [Output('profile-{}-input'.format(x), 'value') for x in ['first', 'last']],
    [Input('profile-trigger', 'children')]
)
def profile_values(trigger):
    """
    triggered by loading the change or saving new values

    loads values from user to database
    user must be logged in
    """
    if not trigger:
        return no_update, no_update, 'First: ', 'Last: ', 'Email:', '', ''
    if current_user.is_authenticated:
        return (
            no_update,
            no_update,
            ['First: ', html.Strong(current_user.first)],
            ['Last: ', html.Strong(current_user.last)],
            ['Email: ', html.Strong(current_user.email)],
            current_user.first,
            current_user.last
        )
    return login_alert, '/login', 'First: ', 'Last: ', 'Email:', '', ''


# function to validate changes input
@app.callback(
    [Output('profile-' + x, 'valid') for x in ['first-input', 'last-input', 'password-input', 'password-confirm']] + \
    [Output('profile-' + x, 'invalid') for x in ['first-input', 'last-input', 'password-input', 'password-confirm']] + \
    [Output('profile-' + x, 'color') for x in ['-password-input-formtext', '-password-confirm-formtext']] + \
    [Output('profile-submit', 'disabled')],
    [Input('profile-' + x, 'value') for x in ['first-input', 'last-input', 'password-input', 'password-confirm']]
)
def profile_validate(first, last, password, confirm):
    disabled = True
    bad = ['', None]
    values = [first, last, password, confirm]
    valids = [False for x in range(4)]
    invalids = [False for x in range(4)]
    colors = ['secondary', 'secondary']

    # if all are invalid
    if sum([x in bad for x in values]) == 4:
        return valids + invalids + colors + [disabled]

    # first name
    i = 0
    if first in bad:
        pass
    else:
        if isinstance(first, str):
            valids[i] = True
        else:
            invalids[i] = True
            colors[0] = 'danger'

    # last name
    i = 1
    if last in bad:
        pass
    else:
        if isinstance(last, str):
            valids[i] = True
        else:
            invalids[i] = True
            colors[1] = 'danger'

    i = 2
    if password in bad:
        pass
    else:
        if isinstance(password, str):
            valids[i] = True
            i = 3
            if confirm == password:
                valids[i] = True
            else:
                invalids[i] = True
        else:
            invalids[i] = True

    # if all inputs are either valid or empty, enable the button
    if sum([1 if (v == False and inv == False) or (v == True and inv == False) else 0 for v, inv in
            zip(valids, invalids)]) == 4:
        disabled = False

    return valids + invalids + colors + [disabled]


# function to save changes
@app.callback(
    [Output('profile-alert', 'children'),
     Output('profile-trigger', 'children')],
    [Input('profile-submit', 'n_clicks')],
    [State('profile-{}-input'.format(x), 'value') for x in ['first', 'last', 'password']]
)
def profile_save_changes(n_clicks, first, last, password):
    """
    change profile values to values in inputs

    if password is blank, pull the current password and submit it
    assumes all inputs are valid and checked by validator callback before submitting (enforced by disabling button otherwise)
    """
    if n_clicks is not None:
        try:
            email = current_user.email
        except AttributeError:
            return failure_alert, 0

        if change_user(first, last, email, engine):
            if password not in ['', None]:
                change_password(email, password, engine)
            if not send_profile_change(email, first):
                return failure_alert, 0

            return success_alert, 1

        return failure_alert, 0
    else:
        return '', ''


# function to save changes
@app.callback(
    [Output('profile-alert-delete', 'children'),
     Output('profile-delete-trigger', 'children')],
    [Input('profile-delete', 'n_clicks')]
)
def profile_delete(n_clicks):
    """
    Delete account
    """
    if n_clicks is not None and n_clicks > 0:
        email = current_user.email
        first = current_user.first

        if del_user(email, engine):
            if send_delete_confirmation(email, first):
                logger.info("Confirmation sent to " + email + " " + first)
            else:
                logger.warning("Confirmation NOT sent to " + email + " " + first)
            return success_delete, 1

        return failure_delete, 0
    else:
        return no_update, no_update


@app.callback(
    Output('redirect-trigger', 'children'),
    [Input('profile-delete-trigger', 'children')]
)
def register_success(value):
    if value == 1:
        time.sleep(2)
        return dcc.Location(pathname='/home', id="redirect")
