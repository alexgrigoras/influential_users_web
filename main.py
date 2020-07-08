import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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
from server import app

header = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand([html.Img(src="static/images/logo.png", height="20px"), " Influential Users"],
                            href="/home"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/home", style={"color": "white"})),
                    dbc.NavItem(dbc.NavLink("Analysis", href="/analysis", style={"color": "white"})),
                    dbc.NavItem(dbc.NavLink(id='user-name', href='/profile', style={"color": "white"})),
                    dbc.NavItem(dbc.NavLink('Login', id='user-action', href='Login', style={"color": "white"}))
                ]
            )
        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

app.layout = html.Div(
    [
        header,
        html.Div(
            [
                dbc.Container(
                    id='page-content'
                )
            ]
        ),
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
    elif pathname == '/' or pathname == '/home' or pathname == '/home':
        return home.layout()
    elif pathname == '/profile' or pathname == '/profile':
        return profile.layout()
    elif pathname == '/analysis' or pathname == '/analysis':
        return analysis.layout()

    return html.Div(['404 - That page does not exist.', html.Br(), dcc.Link('Login', href='/login')])


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def profile_link(content):
    """
    returns a navbar link to the user profile if the user is authenticated
    """
    if current_user.is_authenticated:
        return html.Div("[" + current_user.first + "]")
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
        return 'Logout', '/logout'
    else:
        return 'Login', '/login'


if __name__ == '__main__':
    ml = MessageLogger('werkzeug')
    handler = ml.get_handler()
    app.logger.addHandler(handler)
    app.run_server(host='0.0.0.0', port=5000, debug=False)
