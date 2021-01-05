import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from server import app, engine
from flask_login import current_user
from dash.dependencies import Input, Output, State

home_login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='home-url', refresh=True, pathname='/home')


def layout():
    return dbc.Row(
        dbc.Col(
            children=[
                location,

                # Header
                html.Header([
                    html.Div("", className="overlay"),
                    dbc.Container([
                        html.Div([
                            html.Div(
                                [
                                    html.H1("SOCIAL MEDIA INFLUENCERS MARKETING PLATFORM", className="mb-10",
                                            style={"margin": "20px"}),
                                    html.Br(),
                                    dbc.Container(
                                        html.Form(html.Button("Sign Up", type="submit", id="sign_up_button",
                                                              className="btn btn-block btn-lg btn-primary col-md-3",
                                                              style={"margin-left": "auto", "margin-right": "auto",
                                                                     "visibility": "visible"}),
                                                  action="/register"),
                                        className="container-fluid",
                                    )
                                ],
                                className="col-xl-9 mx-auto"
                            ),
                        ], className="row")
                    ], className="container")
                ], className="masthead text-white text-center"
                ),

                # Icons Grid
                html.Section([
                    dbc.Container([
                        dbc.Row([
                            html.Div(
                                html.Div([
                                    html.Div(html.I("", className="icon-screen-desktop m-auto text-primary"),
                                             className="features-icons-icon d-flex"),
                                    html.H3("Fully Responsive"),
                                    html.P("This theme will look great on any device, no matter the size!",
                                           className="lead mb-0")
                                ],
                                    className="features-icons-item mx-auto mb-5 mb-lg-0 mb-lg-3"
                                ),
                                className="col-lg-4"
                            ),
                            html.Div(
                                html.Div([
                                    html.Div(html.I("", className="icon-layers m-auto text-primary"),
                                             className="features-icons-icon d-flex"),
                                    html.H3("Fully Responsive"),
                                    html.P("This theme will look great on any device, no matter the size!",
                                           className="lead mb-0")
                                ],
                                    className="features-icons-item mx-auto mb-5 mb-lg-0 mb-lg-3"
                                ),
                                className="col-lg-4"
                            ),
                            html.Div(
                                html.Div([
                                    html.Div(html.I("", className="icon-check m-auto text-primary"),
                                             className="features-icons-icon d-flex"),
                                    html.H3("Fully Responsive"),
                                    html.P("This theme will look great on any device, no matter the size!",
                                           className="lead mb-0")
                                ],
                                    className="features-icons-item mx-auto mb-5 mb-lg-0 mb-lg-3"
                                ),
                                className="col-lg-4"
                            )
                        ], className="Row")
                    ], className="container")
                ], className="features-icons bg-light text-center"
                ),

                # Image showcases
                html.Section([
                    html.Div([
                        html.Div([
                            html.Div("", className="col-lg-6 order-lg-2 text-white showcase-img",
                                     style={"background-image": "url('assets/img/bg-showcase-1.jpg')"}),
                            html.Div([
                                dbc.Container([
                                    html.H3("Fully Responsive Design"),
                                    html.P(
                                        "When you use a theme created by Start Bootstrap, you know that the theme will look great on any device, whether it's a phone, tablet, or desktop the page will behave responsively!",
                                        className="lead mb-0")
                                ])
                            ], className="col-lg-6 order-lg-1 my-auto showcase-text")
                        ], className="row no-gutters"),

                        html.Div([
                            html.Div("", className="col-lg-6 text-white showcase-img",
                                     style={"background-image": "url('assets/img/bg-showcase-2.jpg')"}),
                            html.Div([
                                dbc.Container([
                                    html.H3("Updated For Bootstrap 4"),
                                    html.P(
                                        "Newly improved, and full of great utility classes, Bootstrap 4 is leading the way in mobile responsive web development! All of the themes on Start Bootstrap are now using Bootstrap 4!",
                                        className="lead mb-0")
                                ])
                            ], className="col-lg-6 my-auto showcase-text")
                        ], className="row no-gutters"),

                        html.Div([
                            html.Div("", className="col-lg-6 order-lg-2 text-white showcase-img",
                                     style={"background-image": "url('assets/img/bg-showcase-3.jpg')"}),
                            html.Div([
                                dbc.Container([
                                    html.H3("Easy to Use & Customize"),
                                    html.P(
                                        "Landing Page is just HTML and CSS with a splash of SCSS for users who demand some deeper customization options. Out of the box, just add your content and images, and your new landing page will be ready to go!",
                                        className="lead mb-0")
                                ])
                            ], className="col-lg-6 order-lg-1 my-auto showcase-text")
                        ], className="row no-gutters"),

                    ], className="container-fluid p-0"),
                ],
                    className="showcase"
                ),

            ]
        ),
    )


@app.callback(
    Output('sign_up_button', 'style'),
    [Input('sign_up_button', 'n_clicks')]
)
def register_wait_and_reload(clicks):
    if current_user.is_authenticated:
        return {"visibility": "hidden"}
    else:
        return {"margin-left": "auto", "margin-right": "auto", "visibility": "visible"}
