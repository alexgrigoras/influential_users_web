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

header = html.Header([
    html.Div("", className="overlay"),
    dbc.Container([
        html.Div([
            html.Div(
                [
                    html.H1("INFLUENTIAL USERS",
                            className="mb-10", style={"margin-top": "20px", "font-weight": "bold",
                                                      "text-shadow": "2px 2px grey"}),
                    html.H1("Marketing Platform",
                            className="mb-10",
                            style={"margin-bottom": "20px", "text-shadow": "2px 2px grey"}),
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
], className="masthead text-white text-center")

icons_grid = html.Section([
    dbc.Container([
        dbc.Row([
            html.Div(
                html.Div([
                    html.Div(html.I("", className="icon-magic-wand m-auto text-primary"),
                             className="features-icons-icon d-flex"),
                    html.H3("Easy Influencers Discovery"),
                    html.P("Find the best-suited influencers for the specified domain",
                           className="lead mb-0")
                ],
                    className="features-icons-item mx-auto mb-5 mb-lg-0 mb-lg-3"
                ),
                className="col-lg-4"
            ),
            html.Div(
                html.Div([
                    html.Div(html.I("", className="icon-social-youtube m-auto text-primary"),
                             className="features-icons-icon d-flex"),
                    html.H3("YouTube multimedia platform"),
                    html.P("Uses data from the well-known multimedia platform",
                           className="lead mb-0")
                ],
                    className="features-icons-item mx-auto mb-5 mb-lg-0 mb-lg-3"
                ),
                className="col-lg-4"
            ),
            html.Div(
                html.Div([
                    html.Div(html.I("", className="icon-graph m-auto text-primary"),
                             className="features-icons-icon d-flex"),
                    html.H3("Multiple analysis algorithms"),
                    html.P("Using multiple analysis algorithms for getting the best results",
                           className="lead mb-0")
                ],
                    className="features-icons-item mx-auto mb-5 mb-lg-0 mb-lg-3"
                ),
                className="col-lg-4"
            )
        ], className="Row")
    ], className="container")
], className="features-icons bg-light text-center")

image_showcases = html.Section([
    html.Div([
        html.Div([
            html.Div("", className="col-lg-4 order-lg-2 text-white showcase-img",
                     style={"background-image": "url('assets/img/interface.png')"}),
            html.Div([
                dbc.Container([
                    html.H3("Easy application utilization"),
                    html.P(
                        "The web platform is divided between the dashboard (where all the analyzed "
                        "data can be seen and interpreted) and the analysis (where the influencers can "
                        "be searched using specified information)",
                        className="lead mb-0")
                ])
            ], className="col-lg-4 order-lg-1 showcase-text")
        ], className="row no-gutters justify-content-center align-items-center"),

        html.Div([
            html.Div("", className="col-lg-4 text-white showcase-img",
                     style={"background-image": "url('assets/img/intro.png')"}),
            html.Div([
                dbc.Container([
                    html.H3("Discover data from YouTube"),
                    html.P(
                        "The application retrieves data from the YouTube platform and creates a graph "
                        "network with user connections",
                        className="lead mb-0")
                ])
            ], className="col-lg-4 my-auto showcase-text")
        ], className="row no-gutters justify-content-center align-items-center"),

        html.Div([
            html.Div("", className="col-lg-4 order-lg-2 text-white showcase-img",
                     style={"background-image": "url('assets/img/business-img.png')"}),
            html.Div([
                dbc.Container([
                    html.H3("Select the right Influencer"),
                    html.P(
                        "Select the best-suited influencer by analyzing the graph and the list of the "
                        "most "
                        "influential users for the specified domain",
                        className="lead mb-0")
                ])
            ], className="col-lg-4 order-lg-1 my-auto showcase-text")
        ], className="row no-gutters justify-content-center align-items-center"),

    ], className="container-fluid p-0"),
], className="showcase")


def layout():
    return dbc.Row(
        dbc.Col(
            children=[
                location,
                # Header
                header,
                # Icons Grid
                icons_grid,
                # Image showcases
                image_showcases
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
