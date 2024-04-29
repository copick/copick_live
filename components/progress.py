from dash_iconify import DashIconify
import dash_bootstrap_components as dbc


def layout():
    """
    Returns the layout stats
    """
    header = dbc.Card([
                        dbc.CardHeader([
                            DashIconify(icon="ri:progress-3-fill", width=25, style={"margin": "5px"}),
                            'Progress',
                            ],
                            style={"font-weight": "bold"}
                        ),
                        dbc.Label(id='total-labeled', children='Labeled 100 out of 1000 tomograms', style={'margin-top': '5px', 'margin-left': '15px', 'margin-bottom': '-5px'}),
                        dbc.CardBody([dbc.Progress(id='progress-bar', label="0%", value=0)])
                    ],
                    style={"height": '22vh'})
    return header