
from dash import html
import dash_bootstrap_components as dbc

def layout():
    """
    Returns the layout for the header
    """
    header = dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(
                                        id="logo",
                                        src='assets/czii.png',
                                        height="60px",
                                    ),
                                    md="auto",
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H3("ML Challenge  |   Pickathon Live Updates"),
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
                    ],
                    fluid=True,
                ),
                dark=True,
                color="dark",
                sticky="top",
            )
    return header