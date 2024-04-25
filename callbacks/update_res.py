import plotly.express as px
import dash_bootstrap_components as dbc
import json

from utils.data_utils import dataset, copick_config_file, id2key, COUNTER_FILE_PATH
from dash import (
    Input,
    Output,
    callback,
    State,
)

def candidate_list(i, j):
    return  dbc.ListGroupItem("{} (labeled {} times)".format(id2key[i], j))

def ranking_list(i, j):
    return  dbc.ListGroupItem("{} {} tomograms".format(i, j))


@callback(
    Output("modal-help", "is_open"),
    Input("button-help", "n_clicks"),
    State("modal-help", "is_open"),
    prevent_initial_call=True
)
def toggle_help_modal(n_clicks, is_open):
    return not is_open


@callback(
    Output("download-json", "data"),
    Input("btn-download", "n_clicks"),
    State("username", "value"),
    prevent_initial_call=True,
)
def download_json(n_clicks, input_value):   
    filename = 'copick_config_' + '_'.join(input_value.split('.')) + '.json'
    copick_config_file["user_id"] = input_value
    return dict(content=json.dumps(copick_config_file), filename=filename)


@callback(
    Output("download-txt", "data"),
    Input("download-json", "data"),
    State("username", "value"),
    prevent_initial_call=True,
)
def download_txt(json_data, input_value):
    with open(COUNTER_FILE_PATH) as f:
        counter = json.load(f)
    
    if counter['repeat'] == 2:
        counter['start'] += counter['tasks_per_person']
        counter['repeat'] = 0

    counter['repeat'] += 1
    task_contents = '\n'.join(id2key[counter['start']:counter['start']+counter['tasks_per_person']])
    task_filename = 'task_recommendation_' + '_'.join(input_value.split('.')) + '.txt' 

    with open(COUNTER_FILE_PATH, 'w') as f:
        f.write(json.dumps(counter, indent=4))   
    
    return dict(content=task_contents, filename=task_filename)


@callback(
    Output('proteins-histogram', 'figure'),
    Output('waitlist', 'children'),
    Output('rank', 'children'),
    Output('total-labeled', 'children'),
    Output('progress-bar', 'value'),
    Output('progress-bar', 'label'),
    Input('interval-component', 'n_intervals')
)
def update_histogram(n):
    dataset.refresh()
    data = dataset.fig_data()
    #print(data)
    fig = px.bar(x=data['name'], 
                 y=data['count'], 
                 labels={'x': '', 'y':'# of people picked'}, 
                 text_auto=True,
                 color = data['colors'],
                 )
    fig.update(layout_showlegend=False)
    candidates = dataset.candidates(10, random_sampling=False) 
    #print(f'candidates\n{candidates}')
    num_per_person_ordered = dataset.num_per_person_ordered 
    label = f'Labeled {len(dataset.tomos_picked)} out of 1000 tomograms'
    bar_val = len(dataset.tomos_picked)/1000*100
    
    return fig, \
           dbc.ListGroup([candidate_list(i, j) for i, j in candidates.items()], flush=True), \
           dbc.ListGroup([ranking_list(i, j) for i, j in num_per_person_ordered.items()], numbered=True), \
           [label], \
           bar_val, \
           f'{bar_val}%'

