import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from utilities.auth import layout_auth

home_login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='home-url', refresh=True, pathname='/home')


def layout():
    return dbc.Row(
        dbc.Col(
            [
                location,
                html.H3('Welcome to the home page!', style={"textAlign": "center"}),
                html.Br(),
                html.Img(src='/static/images/influential_users.png', width="100%")
            ],
            width=10,
            align="center"
        ),
        justify="center"
    )
