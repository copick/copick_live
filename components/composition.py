import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="vscode-icons:folder-type-component", width=30, style={"margin": "3px"}),
                            'Labeled object types per tomogram',
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        dbc.CardBody(id='composition', style={'overflowY': 'scroll'}),
                    ],
                   style={"height": "87vh"},
                    )