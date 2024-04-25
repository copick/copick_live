from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([DashIconify(icon="noto-v1:trophy", width=25, style={"margin": "5px"}), 
                                        'Annotators ranking'
                                        ], 
                                        style={"font-weight": "bold"}
                                        ),
                        dcc.Loading(
                            id="loading-annotators",
                            children=[html.Div([dbc.CardBody(id='rank'),])],
                            type="circle",
                        )
                    ],
                    style={"height": '100%'})