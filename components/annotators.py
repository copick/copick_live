import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([DashIconify(icon="noto-v1:trophy", width=25, style={"margin": "5px"}), 
                                        'Annotators ranking'
                                        ], 
                                        style={"font-weight": "bold"}
                                        ),
                        dbc.CardBody(id='rank'),
                    ],
                    style={"height": '100%'})