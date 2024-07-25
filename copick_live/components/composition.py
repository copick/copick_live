import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash import html, dcc


roundbutton = {
    "border": 'blue',
    "border-radius": "100%",
    "padding": 0,
    "backgroundColor": 'transparent',
    "color": "blue",
    "textAlign": "center",
    "display": "block",
    "fontSize": 20,
    "height": 40,
    "width": 40,
    "margin": 10
}

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="vscode-icons:folder-type-component", width=30, style={"margin": "3px"}),
                            'Evaluation',
                            dbc.Button('Refresh List', 
                                        id="refresh-button", 
                                        color="primary",  
                                        style = {"text-transform": "none", "fontSize": "0.85em", "width": "25%","height": "85%", "margin-left": "40%"},
                                    )
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        dbc.CardBody(id='card-tomogram-evaluation', 
                                     children=[
                                         dcc.Loading(
                                             id="loading-composition",
                                             children=[html.Div(id='composition')],
                                             type="default",
                                         )
                                     ], 
                                     style={'overflowY': 'scroll'}
                                ),
                    ],
                   style={"height": "87vh"},
                )
