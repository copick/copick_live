import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from collections import defaultdict
import argparse
from copick_live.components.header import layout as header
from copick_live.config import get_config
from copick_live.components.project_explorer import layout as project_explorer

def create_app(config_path=None):
    config = get_config(config_path)
    external_stylesheets = [
        dbc.themes.BOOTSTRAP,
        "assets/header-style.css",
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
        "https://use.fontawesome.com/releases/v5.10.2/css/all.css",
    ]

    app = Dash(__name__, external_stylesheets=external_stylesheets)

    browser_cache = html.Div(
        id="no-display",
        children=[
            dcc.Interval(
                id="interval-component",
                interval=20 * 1000,  # clientside check in milliseconds, 20s
                n_intervals=0,
            ),
            dcc.Store(id="tomogram-index", data=""),
            dcc.Store(id="keybind-num", data=""),
            dcc.Store(id="run-dt", data=defaultdict(list)),
        ],
    )

    app.layout = html.Div(
        [
            header(),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H2("CoPick Project Explorer"),
                                    project_explorer(),
                                ],
                                width=12,
                            ),
                        ],
                        className="mb-4",
                    ),
                ],
                fluid=True,
            ),
            html.Div(browser_cache),
        ],
    )

    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the experimental Dash application with a specific config path.')
    parser.add_argument('--config-path', type=str, help='Path to the configuration file.', required=False)
    args = parser.parse_args()

    dash_app = create_app(config_path=args.config_path)
    dash_app.run_server(host="0.0.0.0", port=8000, debug=True)
