import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from collections import defaultdict

from callbacks.update_res import *  
from components.header import layout as header
from components.progress import layout as tomo_progress
from components.proteins import layout as protein_sts
from components.waitlist import layout as unlabelled_tomos
from components.annotators import layout as ranking
from components.composition import layout as composition
from components.popups import layout as popups


external_stylesheets = [dbc.themes.BOOTSTRAP, 
                        "assets/header-style.css", 
                        "https://codepen.io/chriddyp/pen/bWLwgP.css",
                        "https://use.fontawesome.com/releases/v5.10.2/css/all.css"] 

app = Dash(__name__, external_stylesheets=external_stylesheets)

browser_cache =html.Div(
        id="no-display",
        children=[
            dcc.Interval(
                id='interval-component',
                interval=20*1000, # clientside check in milliseconds, 10s
                n_intervals=0
                ),
            dcc.Store(id='tomogram-index', data=''),
            dcc.Store(id='keybind-num', data=''),
            dcc.Store(id='run-dt', data=defaultdict(list))
        ],
    )


app.layout = html.Div(
    [
        header(),
        popups(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col([tomo_progress(),
                                 unlabelled_tomos()
                                 ], 
                                 width=3), 
                        dbc.Col(ranking(), width=3),
                        dbc.Col(composition(), width=3),
                        dbc.Col(protein_sts(), width=3),
                    ],
                    justify='center',
                    className="h-100",
                ),
            ],
            fluid=True,
        ),
        html.Div(browser_cache)
    ],
)




if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8000, debug=False)

