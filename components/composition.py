import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="icon-park-twotone:composition", width=30, style={"margin": "3px"}),
                            'Proteins labeled per tomogram',
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        dbc.CardBody(id='composition', style={'overflowY': 'scroll'}),
                    ],
                   style={"height": "87vh"},
                    )