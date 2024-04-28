import os
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

from callbacks.update_res import *  
from components.header import layout as header
from components.progress import layout as tomo_progress
from components.proteins import layout as protein_sts
from components.waitlist import layout as unlabelled_tomos
from components.annotators import layout as ranking
from components.composition import layout as composition


external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/header-style.css",]  # need to use bootstrap themes
app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

browser_cache =html.Div(
        id="no-display",
        children=[
            dcc.Interval(
            id='interval-component',
            interval=20*1000, # in milliseconds, 10s
            n_intervals=0
        )
        ],
    )


app.layout = html.Div(
    [
        header(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col([tomo_progress(),
                                 unlabelled_tomos()
                                 ], 
                                 width=2), 
                        dbc.Col(ranking(), width=3),
                        dbc.Col(composition(), width=3),
                        dbc.Col(protein_sts(), width=4),
                    ],
                    justify='center',
                    className="h-60",
                ),
            ],
            fluid=True,
        ),
        html.Div(browser_cache)
    ],
)




if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8000, debug=False)
