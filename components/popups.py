from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from utils.local_dataset import local_dataset
from dash_extensions import EventListener

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



competition_results = [
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '95%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
]



tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Picked points visualization", tab_id="tab-1"),
                dbc.Tab(label="2D Plane Inspection", tab_id="tab-2"),
                #dbc.Tab(label="3D Volume Inspection", tab_id="tab-3"),
            ],
            id="tabs",
            active_tab="tab-1",
        ),
        html.Div([
            dbc.Label("Choose results", id='choose-results', style={'margin-top': '35px', 'margin-left': '7px'}),
            dcc.Dropdown(["Pickathon results"], 'Pickathon results', id='pick-dropdown', style={'width':'42%', 'justify-content': 'center', 'margin-bottom': '0px', 'margin-left': '4px'}),
            dbc.Collapse(id="collapse1",is_open=False, children=dbc.Spinner(dcc.Graph(id='fig1', figure=blank_fig()), spinner_style={"width": "5rem", "height": "5rem"})),
            dbc.Collapse(id="collapse2",is_open=False, children=dbc.Container([dbc.Row(
                                                                                    [ 
                                                                                        dbc.Col([
                                                                                                dbc.Label("Please input your name", style={'margin-top': '-20px'}),
                                                                                                dbc.Input(id='username-analysis', placeholder="e.g., john.doe", type="text", style={'width': '75%'}),
                                                                                                dbc.Label("Please select a particle type", className="mt-3"),
                                                                                                dcc.Dropdown(id='particle-dropdown', style={'width': '87%'}),
                                                                                                dbc.Label("Number of rows", className="mt-3"),
                                                                                                dcc.Input(id="display-row",type="number", placeholder="5", value =5, min=1, step=1),
                                                                                                dbc.Label("Number of columns", className="mt-3"),
                                                                                                dcc.Input(id="display-col",type="number", placeholder="4", value =4, min=1, step=1),
                                                                                                dbc.Label(id='crop-label', children="Image crop size (max 100)", className="mt-3"),
                                                                                                dcc.Input(id="crop-width",type="number", placeholder="30", value =60, min=1, step=1),
                                                                                                dbc.Label("Average ±N neigbor layers", className="mt-3"),
                                                                                                dcc.Input(id="crop-avg", type="number", placeholder="3", value =2, min=0, step=1),
                                                                                                dbc.Label("Page slider (press key < or >)", className="mt-3"),
                                                                                                html.Div(dcc.Slider(
                                                                                                            id='image-slider',
                                                                                                            min=0,
                                                                                                            max=200,
                                                                                                            value = 0,
                                                                                                            step = 1,
                                                                                                            updatemode='drag',
                                                                                                            tooltip={"placement": "top", "always_visible": True},
                                                                                                            marks={0: '0', 199: '199'},
                                                                                                        ), style={'width':'72%', 'margin-top': '10px'}),
                                                                                            ],
                                                                                            width=3,
                                                                                            align="center"
                                                                                        ),
                                                                                        dbc.Col([
                                                                                                    html.Div(id='output-image-upload',children=[], style={"height":"70vh", 'overflowY': 'scroll'}),
                                                                                                    # dcc.Graph(id='fig2', 
                                                                                                    #        figure=blank_fig(),
                                                                                                    #        style={
                                                                                                    #             "width": "100%",
                                                                                                    #             "height": "100%",
                                                                                                    #         })
                                                                                                ], 
                                                                                                width=5,
                                                                                                align="top",
                                                                                        ),
                                                                                        dbc.Col([
                                                                                            dbc.Row([
                                                                                                        dbc.Col(dbc.Row(dbc.Button('Select All', id='select-all-bttn', style={'width': '50%'}, color='primary', className="me-1"), justify='end')),
                                                                                                        dbc.Col(dbc.Row(dbc.Button('Unselect All', id='unselect-all-bttn', style={'width': '50%'}, color='primary', className="me-1"), justify='start'))
                                                                                                    ],
                                                                                                    justify='evenly',
                                                                                                    style={'margin-bottom': '40px'}
                                                                                                    ),
                                                                                            dbc.Row([
                                                                                                        dbc.Col(dbc.Row(dbc.Button('(D) Reject', id='reject-bttn', style={'width': '50%'}, color='danger', className="me-1"), justify='end')),
                                                                                                        dbc.Col(dbc.Row(dbc.Button('(A) Accept', id='accept-bttn', style={'width': '50%'}, color='success', className="me-1"), justify='start'))
                                                                                                    ],
                                                                                                    justify='evenly',
                                                                                                    style={'margin-bottom': '40px'}
                                                                                                    ),
                                                                                            dbc.Row([
                                                                                                        dbc.Col(dbc.Row(dbc.Button('(S) Assign', id='assign-bttn', style={'width': '25%', 'margin-left':'90px'}, color='primary', className="me-1"), justify='start')),
                                                                                                        #dbc.Col(dbc.Row(dbc.Button('Select All', id='select-all-bttn', style={'width': '50%'}, color='primary', className="me-1"), justify='start')),
                                                                                                        #dbc.Col(dbc.Row(dbc.ListGroup([dbc.ListGroupItem(f'({str(i+1)}) {k}') for i,k in enumerate(local_dataset._im_dataset['name'])]), justify='start'))
                                                                                                    ],
                                                                                                    justify='evenly',
                                                                                                    style={'margin-bottom': '5px'}
                                                                                                    ),
                                                                                            dbc.Row([dbc.Col(dbc.Row(dcc.Dropdown(id='assign-dropdown', options={k:k for k in local_dataset._im_dataset['name']}, style={'width': '75%', 'margin-left':'-10px'}), justify='end'))
                                                                                                     ],
                                                                                                     justify='evenly')
                                                                                        ], 
                                                                                        width=4, 
                                                                                        align="right",
                                                                                        ),
                                                                                    ],
                                                                                    justify='center',
                                                                                    align="center",
                                                                                    className="h-100",
                                                                                ),
                                                                            ],
                                                                            fluid=True,
                                                                        ), 
                ),                                                       
                #dbc.Collapse(id="collapse3",is_open=False, children=dcc.Graph(id='fig3', figure=blank_fig())),
                EventListener(
                    events=[
                        {
                            "event": "keydown",
                            "props": ["key", "ctrlKey", "ctrlKey"],
                        }
                    ],
                    id="keybind-event-listener",
                ),
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
                    dbc.ModalHeader(dbc.ModalTitle("Submission Results")),
                    dbc.ModalBody(id='modal-body-results', children=competition_results),
                ], 
                id="modal-results",
                is_open=False,
                size="xl"
            ),
        dbc.Modal([
                    #dbc.ModalHeader(dbc.ModalTitle("Tomogram Evaluation")),
                    dbc.ModalBody(id='modal-body-evaluation', children=tabs),
                ], 
                id="modal-evaluation",
                is_open=False,
                centered=True,
                size='xl'
            ),
    ])
