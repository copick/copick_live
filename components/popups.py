from dash import html, dcc
import dash_bootstrap_components as dbc

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

evaluations = []

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
                    dbc.ModalHeader(dbc.ModalTitle("Tomogram Evaluation")),
                    dbc.ModalBody(id='modal-body-evaluation', children=evaluations),
                ], 
                id="modal-evaluation",
                is_open=False,
                size="xl"
            ),
    ])
