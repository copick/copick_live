from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                dbc.CardHeader([
                    DashIconify(icon="ic:baseline-done-outline", width=23, style={"margin": "5px"}),
                    'Labeled objects',
                ], 
                style={"font-weight": "bold"}
                ),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-proteins-histogram",
                        children=[dcc.Graph(id='proteins-histogram')],
                        type="default",
                    )
                ])
            ],
            style={"height": '87vh'}
            )
