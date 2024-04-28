import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="material-symbols-light:microbiology-outline", width=30, style={"margin": "3px"}),
                            'Waitlist (labeled by < 2 people)',
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        dbc.CardBody(id='waitlist', style={'overflowY': 'scroll'}),
                    ],
                    style={"height": '70vh'}
                    )