
from dash import html
import dash_bootstrap_components as dbc


button_start = dbc.Button(
    "Getting Started",
    #outline=True,
    color="primary",
    id="button-help",
    className="me-1",
    style={"text-transform": "none", "fontSize": "0.85em"},
)

button_results = dbc.Button(
    "Submission Results",
    #outline=True,
    color="primary",
    id="button-results",
    className="me-1",
    style={"text-transform": "none", "fontSize": "0.85em"},
)

def layout():
    header= dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                id="logo",
                                src='assets/czii.png',
                                height="40px",
                            ),
                            md="auto",
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H3("CZII ML Challenge | Pickathon Live Updates"),
                                        #html.P("Pickathon Live Updates"),
                                    ],
                                    id="app-title",
                                )
                            ],
                            md=True,
                            align="center",
                        ),
                    ],
                    align="center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.NavbarToggler(id="navbar-toggler"),
                                dbc.Collapse(
                                    dbc.Nav(
                                        [
                                            dbc.NavItem(button_start),
                                            dbc.NavItem(button_results),
                                        ],
                                        navbar=True,
                                    ),
                                    id="navbar-collapse",
                                    navbar=True,
                                ),
                            ],
                            md=2,
                        ),
                    ],
                    align="center",
                ), 
            ],
            fluid=True,
        ),
        dark=True,
        color="dark",
        sticky="top",
    )
    return header