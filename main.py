import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_login import current_user

from application.message_logger import MessageLogger
from pages import (
    home,
    dashboard,
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


menu_bar = [
    dbc.NavLink("Home", href="/home", className="ml-auto"),
    dbc.NavLink("Dash", href="/dashboard", style={"margin": "0"}),
    dbc.NavLink("Analysis", href="/analysis", style={"margin": "0"}),
    html.Div(id='dropdown-container', style={"margin": "0"}),
    dbc.NavLink('Login', id='user-action', href='/login', style={"margin": "0"}),
]

header = dbc.Navbar(
    dbc.Container([
        html.A(
            children=[
                html.Img(src="static/images/logo.png", height="40px"),
                dbc.NavbarBrand("socialinfluencers", className="ml-2"),
            ],
            href="/home",
            className="navbar-brand"
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(menu_bar, id="navbar-collapse", navbar=True, className="mx-auto"),
    ]),
    color="primary",
    dark=True,
    className="ml-auto"
)

footer = html.Footer(
    children=[
        dbc.Container(
            dbc.Row([
                html.Div([
                    html.Ul([
                        html.Li(html.A("About", href="#"), className="list-inline-item"),
                        html.Li("·", className="list-inline-item"),
                        html.Li(html.A("Contact", href="#"), className="list-inline-item"),
                        html.Li("·", className="list-inline-item"),
                        html.Li(html.A("Terms of use", href="#"), className="list-inline-item"),
                    ], className="list-inline mb-2"),
                    html.P('socialinfluencers © 2020. All Rights Reserved.', className="text-muted small mb-4 mb-lg-0")
                ], className="col-lg-6 h-100 text-center text-lg-left my-auto"
                ),
                html.Div([
                    html.Ul([
                        html.Li(html.A(html.I("", className="fab fa-facebook fa-2x fa-fw"), href="#"),
                                className="list-inline-item mr-3"),
                        html.Li(html.A(html.I("", className="fab fa-twitter-square fa-2x fa-fw"), href="#"),
                                className="list-inline-item mr-3"),
                        html.Li(html.A(html.I("", className="fab fa-instagram fa-2x fa-fw"), href="#"),
                                className="list-inline-item mr-3"),
                    ], className="ist-inline mb-0")
                ], className="col-lg-6 h-100 text-center text-lg-right my-auto"
                ),
            ])
        )
    ],
    className="footer bg-light",
)

app.layout = html.Div(
    [
        header,
        html.Div(
            html.Div(
                id='page-content',
            ),
            className="wrapper bg-light"
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
    elif pathname == '/dashboard':
        return dashboard.layout()
    elif pathname == '/profile':
        return profile.layout()
    elif pathname == '/analysis':
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
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-user fa-sm fa-fw mr-2 text-gray-400"),
                    "Profile"
                ], href='/profile'),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"),
                    "Logout"
                ], href="/logout"),
            ],
            className="mx-auto",
            nav=True,
            in_navbar=True,
            style={"list-style-type": "none"},
            label=current_user.first
        )
        return new_dropdown
    else:
        return ''


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output('user-action', 'children'),
     Output('user-action', 'href'),
     Output('user-action', 'disabled')],
    [Input('page-content', 'children')])
def user_logout(user_input):
    """
    returns a navbar link to /logout or /login, respectively, if the user is authenticated or not
    """
    if current_user.is_authenticated:
        return '', '', 'True'
    else:
        return 'Login', '/login', None


if __name__ == '__main__':
    ml = MessageLogger('werkzeug')
    handler = ml.get_handler()
    app.logger.addHandler(handler)
    app.run_server(host='0.0.0.0', port=5000, debug=False)
