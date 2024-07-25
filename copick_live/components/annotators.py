import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash import dcc

def layout():
    return dbc.Card([
                        dbc.CardHeader([DashIconify(icon="noto-v1:trophy", width=25, style={"margin": "5px"}), 
                                        'Annotators ranking'
                                        ], 
                                        style={"font-weight": "bold"}
                                        ),
                        dcc.Loading(
                            id="loading-annotators",
                            children=[dbc.CardBody(id='rank', style={'overflowY': 'scroll'})],
                            type="default",
                        )
                    ],
                    style={"height": '87vh'}
                    )
