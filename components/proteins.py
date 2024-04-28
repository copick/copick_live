from dash import dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="ic:baseline-done-outline", width=23, style={"margin": "5px"}),
                            'Labeled proteins',
                        ], 
                        style={"font-weight": "bold"}
                        ),
                        dbc.CardBody([dcc.Graph(id='proteins-histogram')])
                    ],
                    style={"height": '87vh'}),