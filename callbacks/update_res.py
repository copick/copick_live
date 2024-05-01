import plotly.express as px
import dash_bootstrap_components as dbc
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from utils.data_utils_threading import dataset, dirs, dir2id, COUNTER_FILE_PATH
from dash import (
    html,
    Input,
    Output,
    callback,
    State,
)



# 1st update of the internal states
dataset.refresh()

#Scheduler
scheduler = BackgroundScheduler() # in-memory job stores
scheduler.add_job(func=dataset.refresh, trigger='interval', seconds=20)  # interval should be larger than the time it takes to refresh, o.w. it will be report incomplete stats.
scheduler.start()


def candidate_list(i, j):
    return  dbc.ListGroupItem("{} (labeled by {} person)".format(dirs[i], j))

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
    input_value = '.'.join(input_value.split(' '))
    filename = 'copick_config_' + '_'.join(input_value.split('.')) + '.json'   
    dataset.config_file["user_id"] = input_value
    return dict(content=json.dumps(dataset.config_file, indent=4), filename=filename)


@callback(
    Output("download-txt", "data"),
    Input("btn-download-txt", "n_clicks"),
    #State("username", "value"),
    prevent_initial_call=True,
)
def download_txt(n_clicks):
    with open(COUNTER_FILE_PATH) as f:
        counter = json.load(f)
    
    if counter['repeat'] == 2:
        counter['start'] += counter['tasks_per_person']
        counter['repeat'] = 0

    counter['repeat'] += 1
    task_contents = '\n'.join(dirs[counter['start']:counter['start']+counter['tasks_per_person']])
    task_filename = 'task_recommendation.txt' 

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
def update_results(n):
    data = dataset.fig_data()
    fig = px.bar(x=data['name'], 
                 y=data['count'], 
                 labels={'x': 'Objects', 'y':'Counts'}, 
                 text_auto=True,
                 color = data['name'],
                 color_discrete_map = data['colors'],
                 )
    fig.update(layout_showlegend=False)
    candidates = dataset.candidates(100, random_sampling=False)
    num_per_person_ordered = dataset.num_per_person_ordered 
    label = f'Labeled {len(dataset.tomos_pickers)} out of 1000 tomograms'
    bar_val = round(len(dataset.tomos_pickers)/1000*100, 1)
    
    return fig, \
           dbc.ListGroup([candidate_list(i, j) for i, j in candidates.items()], flush=True), \
           dbc.ListGroup([ranking_list(i, len(j)) for i, j in num_per_person_ordered.items()], numbered=True), \
           [label], \
           bar_val, \
           f'{bar_val}%'


@callback(
    Output('composition', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_results(n):
    progress_list = []
    composition_list = html.Div()
    data = dataset.fig_data()
    l = 1/len(data['colors'])*100
    obj_order = {name:i for i,name in enumerate(data['name'])}
    tomograms = {k:v for k,v in sorted(dataset.tomograms.items(), key=lambda x: dir2id[x[0]])} 
    for tomogram,ps in tomograms.items():
        progress = []
        ps = [p for p in ps if p in obj_order]
        ps = sorted(list(ps), key=lambda x: obj_order[x])
        for p in ps:
            progress.append(dbc.Progress(value=l, color=data['colors'][p], bar=True))
        
        progress_list.append(dbc.ListGroupItem([tomogram, dbc.Progress(progress)]))
    
    composition_list = dbc.ListGroup(progress_list)
    return composition_list