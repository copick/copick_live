
from dash import html
import dash_bootstrap_components as dbc
from .instructions import instructions



button_help = dbc.Button(
    "Get started",
    #outline=True,
    color="primary",
    id="button-help",
    className="me-1",
    style={"text-transform": "none"},
)


help_popup = dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Instructions")),
                    dbc.ModalBody(instructions),
                ], 
                id="modal-help",
                is_open=False,
                size="xl"
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
                                height="50px",
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
                                            dbc.NavItem(button_help),
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
                help_popup  
            ],
            fluid=True,
        ),
        dark=True,
        color="dark",
        sticky="top",
    )
    return header