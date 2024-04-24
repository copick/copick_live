import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def layout():
    return dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="material-symbols-light:microbiology-outline", width=30, style={"margin": "3px"}),
                            'Tomograms waiting to be curated by 2 people',
                            ], 
                            style={"font-weight": "bold"}
                        ),
                        dbc.CardBody(id='waitlist'),
                    ],
                    style={"height": '77.5%'}
                    )