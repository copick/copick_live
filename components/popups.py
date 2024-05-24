from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def blank_fig():
    """
    Creates a blank figure with no axes, grid, or background.
    """
    fig = go.Figure()
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig



instructions = [dcc.Markdown('''
                        Thanks for participating in CZII Pickathon! We highly encourage labeling all the 6 types of prteins in the tomogram.
                        ### Tools installation
                        #### ChimeraX
                        1. Download and install [ChimeraX](https://www.cgl.ucsf.edu/chimerax/download.html) version 1.7.0+
                        2. Download the [copick plugin](https://cxtoolshed.rbvi.ucsf.edu/apps/chimeraxcopick)
                        3. Open ChimeraX and install the copick wheel by typing in the command line: `toolshed install /path/to/your/ChimeraX_copick-0.1.3-py3-none-any.whl` 
                        
                        #### Configuration files
                        Auto-generate the copick configuration file and a tomogram recomendation list for you (5 tomograms per file).    
                        ''', 
                        link_target='_blank'
                        ),
                html.Div(
                        children=[
                            dbc.Input(id='username', placeholder="Please input your name (e.g., john.doe)", type="text"),
                            dbc.Button("Download copick config file", id='btn-download', outline=True, color="primary", className="me-1"),
                            dbc.Button("Download recommendation file", id='btn-download-txt', outline=True, color="primary", className="me-1"),
                            dcc.Download(id="download-json"),
                            dcc.Download(id="download-txt"),
                        ],
                        className="d-grid gap-3 col-4 mx-auto",
                ),    
                dcc.Markdown('''
                            ### Particle picking 
                            The default workflow for ChimeraX should be:  
                            1. Type the command `copick start /path/to/config`. It will take about 2-3 mins to load the entire dataset tree.  
                            2. Open a tomogram by navigating the tree and double-clicking.  
                            3. Select or double click a pre-picked list from the upper table (double click will load the list).    
                            4. Press the ▼ ▼ ▼ button to copy the contents to the "editable" lower table.  
                            5. Select the Copick tab at the top right corner and choose a tool in the `Place Particles` session. Start editing by right click. Your picking results will be automatically saved.  
                            ''')

    ]


tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Points visualization", tab_id="tab-1"),
                dbc.Tab(label="2D Plane Inspection", tab_id="tab-2"),
                dbc.Tab(label="3D Volume Inspection", tab_id="tab-3"),
            ],
            id="tabs",
            active_tab="tab-1",
        ),
        html.Div([
            dbc.Collapse(id="collapse1",is_open=False, children=[html.Div(dcc.Dropdown(["Pickathon results","Embedding model results"], 'Pickathon results', id='pick-dropdown'), style={'width':'30%', 'justify-content': 'right', 'margin-top': '20px'}),
                                                                 dcc.Graph(id='fig1', figure=blank_fig())]),
            dbc.Collapse(id="collapse2",is_open=False, children=dbc.Container([
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col([dcc.Graph(id='fig2', figure=blank_fig()),
                                                                                                dbc.Row([
                                                                                                            dbc.Col(dbc.Row(dbc.Button('Reject', id='prev-im2d', style={'width': '50%'}, disabled=False, color='danger'), justify='end')),
                                                                                                            dbc.Col(dbc.Row(dbc.Button('Accept', id='next-im2d', style={'width': '50%'}, disabled=False, color='success'), justify='start'))
                                                                                                        ],
                                                                                                        justify='evenly'
                                                                                                        ),
                                                                                                 ], 
                                                                                                width=4,
                                                                                                align="center",
                                                                                               ), 
                                                                                        dbc.Col([
                                                                                                 dbc.Label(
                                                                                                        "Please input your name",
                                                                                                        className="mb-3",
                                                                                                        #html_for='image-slider',
                                                                                                    ),
                                                                                                dbc.Input(id='username-eval', placeholder="e.g., john.doe", type="text"),
                                                                                                dbc.Label(
                                                                                                        "Please select a particle type",
                                                                                                        className="mb-3",
                                                                                                        #html_for='image-slider',
                                                                                                    ),
                                                                                                dcc.Dropdown(["apo-ferritin", "beta-amylase","beta-galactosidase", "ribosome", "thyroglobulin",  "virus-like-particle", "membrane-bound-protein"], 'ribosome', id='particle-dropdown'),
                                                                                                dbc.Label("image width", className="mb-3"),
                                                                                                dcc.Input(id="crop_width",type="number", placeholder="30", value =30),
                                                                                                dbc.Label(
                                                                                                        "Image Slider",
                                                                                                        className="mb-3",
                                                                                                        html_for='image-slider',
                                                                                                    ),
                                                                                                dcc.Slider(
                                                                                                        id='image-slider',
                                                                                                        min=0,
                                                                                                        max=200,
                                                                                                        value = 0,
                                                                                                        step = 1,
                                                                                                        updatemode='drag',
                                                                                                        tooltip={"placement": "top", "always_visible": True},
                                                                                                        marks={0: '0', 199: '199'},
                                                                                                    ),
                                                                                            ],
                                                                                            width=4,
                                                                                            align="center"),
                                                                                    ],
                                                                                    justify='center',
                                                                                    align="center",
                                                                                    className="h-100",
                                                                                ),
                                                                            ],
                                                                            fluid=True,
                                                                        ), 
                ),                                                       
                dbc.Collapse(id="collapse3",is_open=False, children=dcc.Graph(id='fig3', figure=blank_fig())),
            ]),
        ]
    )



def layout():
    return html.Div([
        dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("Instructions")),
                    dbc.ModalBody(id='modal-body-help', children=instructions),
                ], 
                id="modal-help",
                is_open=False,
                size="xl"
            ),
        dbc.Modal([
                    #dbc.ModalHeader(dbc.ModalTitle("Tomogram Evaluation")),
                    dbc.ModalBody(id='modal-body-evaluation', children=tabs),
                ], 
                id="modal-evaluation",
                is_open=False,
                size="xl"
            ),
    ])
