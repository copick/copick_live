import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash import dcc

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="material-symbols-light:microbiology-outline", width=30, style={"margin": "3px"}),
                            'Waitlist (labeled by < 2 people)',
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        dcc.Loading(
                            id="loading-waitlist",
                            children=[dbc.CardBody(id='waitlist', style={'overflowY': 'scroll'})],
                            type="default",
                        )
                    ],
                    style={"height": '72vh'}
                    )
