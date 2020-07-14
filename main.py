import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_login import current_user

from application.message_logger import MessageLogger
from pages import (
    home,
    profile,
    analysis
)
# app authentication
from pages.auth_pages import (
    login,
    logout,
    register,
    forgot_password,
    change_password
)
from server import app, server

header = dbc.NavbarSimple(
    children=[
            dbc.NavItem(dbc.NavLink("Home", href="/home", style={"color": "white"})),
            dbc.NavItem(dbc.NavLink("Analysis", href="/analysis", style={"color": "white"})),
            html.Div(id='dropdown-container'),
            dbc.NavItem(dbc.NavLink('Login', id='user-action', href='/login', style={"color": "white"}))
    ],
    brand="Influential Users",
    brand_href="/home",
    color="primary",
    dark=True,
    className="mb-5",
)

footer = html.Footer(
    children=[
        html.Hr(),
        html.Div(html.Span("© 2020 Copyright: Alexandru GRIGORAS", className="text-muted"), className="container")
    ],
    className="footer",
)

app.layout = html.Div(
    [
        header,
        html.Div(
            [
                dbc.Container(
                    id='page-content'
                ),
                html.Br()
            ]
        ),
        footer,
        dcc.Location(id='base-url', refresh=False),
    ]
)


@app.callback(
    Output('page-content', 'children'),
    [Input('base-url', 'pathname')])
def router(pathname):
    """
    routes to correct page based on pathname
    """
    # auth pages
    if pathname == '/login':
        return login.layout()
    elif pathname == '/register':
        return register.layout()
    elif pathname == '/change':
        return change_password.layout()
    elif pathname == '/forgot':
        return forgot_password.layout()
    elif pathname == '/logout':
        return logout.layout()

    # app pages
    elif pathname == '/' or pathname == '/home':
        return home.layout()
    elif pathname == '/profile' or pathname == '/profile':
        return profile.layout()
    elif pathname == '/analysis' or pathname == '/analysis':
        return analysis.layout()

    return html.Div(['404 - That page does not exist.', html.Br(), dcc.Link('Login', href='/login')])


@app.callback(
    Output('dropdown-container', 'children'),
    [Input('page-content', 'children')],
    [State('dropdown-container', 'children')])
def profile_link(content, children):
    """
    returns a navbar link to the user profile if the user is authenticated
    """
    if current_user.is_authenticated:
        new_dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Profile", href='/profile'),
                dbc.DropdownMenuItem("Logout", href="/logout"),
            ],
            nav=True,
            in_navbar=True,
            toggle_style={"color": "white"},
            label=current_user.first
        )
        return new_dropdown
    else:
        return ''


@app.callback(
    [Output('user-action', 'children'),
     Output('user-action', 'href')],
    [Input('page-content', 'children')])
def user_logout(user_input):
    """
    returns a navbar link to /logout or /login, respectively, if the user is authenticated or not
    """
    if current_user.is_authenticated:
        return '', ''
    else:
        return 'Login', '/login'


if __name__ == '__main__':
    ml = MessageLogger('werkzeug')
    handler = ml.get_handler()
    app.logger.addHandler(handler)
    app.run_server(host='0.0.0.0', port=5000, debug=False)
