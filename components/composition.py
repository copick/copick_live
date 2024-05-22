import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash import html


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
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        #dbc.Row(dbc.Button('Refresh', id="refresh-button", outline=True, color="primary", className="me-1", size="sm"), justify="center"),
                        dbc.CardBody(id='card-tomogram-evaluation', 
                                     children=[
                                          html.Div(dbc.Button('Refresh List', 
                                                        id="refresh-button", 
                                                        outline=True, 
                                                        color="primary", 
                                                        className="me-1",  
                                                        style = {"text-transform": "none"}),
                                                    style ={'display': 'flex', 'justify-content': 'center', 'margin': '3px'},
                                                ),
                                         html.Div(id='composition')
                                     ], 
                                     style={'overflowY': 'scroll'}
                                ),
                    ],
                   style={"height": "87vh"},
                )