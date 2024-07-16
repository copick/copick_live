import plotly.express as px
import dash_bootstrap_components as dbc
import json, time
import pandas as pd
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler

import time
from copick_live.utils.copick_dataset import copick_dataset
from copick_live.utils.figure_utils import (
    blank_fig,
    draw_gallery
)
from copick_live.utils.local_dataset import (
    local_dataset, 
    dirs, 
    dir2id, 
    COUNTER_FILE_PATH, 
    #CACHE_ROOT,
)
from dash import (
    html,
    Input,
    Output,
    callback,
    State,
    ALL,
    MATCH,
    ctx,
    dcc,
    no_update
)
from dash.exceptions import PreventUpdate


from dash_iconify import DashIconify
import base64



def submission_list(i,j):
    return  dbc.ListGroupItem("{}:      {}".format(i.split('.json')[0], j))


import io
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    fig = []
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df = df.sort_values(by=['Aggregate_Fbeta'], ascending=False)
            df = df.reset_index(drop=True)
            df['rank'] = df.index
            #df = df[['File', 'Aggregate_Fbeta']]
            dict_df = df.set_index('File')['Aggregate_Fbeta'].to_dict()
            print(dict_df)
            fig = px.scatter(df, x='rank', y='Aggregate_Fbeta', hover_name='File', title='Submitted model ranking')
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df = df.sort_values(by=['Aggregate_Fbeta'], ascending=False)
            df = df[['File', 'Aggregate_Fbeta']]
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return dbc.Card([
                dbc.CardHeader([DashIconify(icon="noto-v1:trophy", width=25, style={"margin": "5px"}), 
                                'Submitted model ranking'
                                ], 
                                style={"font-weight": "bold"}
                                ),
                dbc.CardBody(id='submission-rank', children=dcc.Graph(figure=fig), style={'overflowY': 'scroll'})
            ],
            style={"height": '87vh'}
            )



# 1st update of the internal states
local_dataset.refresh()

#Scheduler
scheduler = BackgroundScheduler() # in-memory job stores
scheduler.add_job(func=local_dataset.refresh, trigger='interval', seconds=20)  # interval should be larger than the time it takes to refresh, o.w. it will be report incomplete stats.
scheduler.start()


roundbutton = {
    "border": 'transparent',
    #"border-radius": "100%",
    "padding": 0,
    "backgroundColor": 'transparent',
    "color": "black",
    "textAlign": "center",
    "display": "block",
    "fontSize": 9,
    "height": 9,
    "width": 9,
    "margin-left": 10,
    "margin-top": 8,
}



def candidate_list(i, j):
    return  dbc.ListGroupItem("{} (labeled by {} person)".format(dirs[i], j))

def ranking_list(i, j):
    return  dbc.ListGroupItem("{} {} tomograms".format(i, j))



############################################## Callbacks ##############################################
@callback(
    Output("modal-help", "is_open"),
    Input("button-help", "n_clicks"),
    State("modal-help", "is_open"),
    prevent_initial_call=True
)
def toggle_help_modal(n_clicks, is_open):
    return not is_open


@callback(
    Output("modal-results", "is_open"),
    Input("button-results", "n_clicks"),
    State("modal-results", "is_open"),
    prevent_initial_call=True
)
def toggle_help_modal(n_clicks, is_open):
    return not is_open


@callback(Output('output-data-upload', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'),
          State('upload-data', 'last_modified')
          )
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@callback(
    Output("tomogram-index", "data"),
    Input({"type": "tomogram-eval-bttn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_tomogram_index(n_clicks):
    if any(n_clicks):
        changed_id = [p['prop_id'] for p in ctx.triggered][0].split(".")[0]
        if "index" in changed_id:
            tomogram_index = json.loads(changed_id)["index"]
            return tomogram_index


@callback(
    Output("collapse1", "is_open"),
    Output("collapse2", "is_open"),
    Input("tabs", "active_tab"),
    prevent_initial_call=True
)
def toggle_analysis_tabs(at):
    if at == "tab-1":
        return True, False
    elif at == "tab-2":
        return False, True


@callback(
    Output("output-image-upload", "children", allow_duplicate=True),
    Output("image-slider", "value"),
    Output("particle-dropdown", "value"),
    Output("modal-evaluation", "is_open"),
    Output("tabs", "active_tab"),
    Output("choose-results", "children"),
    Input("tomogram-index", "data"),
    prevent_initial_call=True
)
def reset_analysis_popup(tomogram_index):
    msg = f"Choose results for {tomogram_index}"
    if tomogram_index is not None:
        return [], 0, None, True, "tab-1", msg
    else:
        return  [], 0, None, False, "tab-1", msg


@callback(
    Output("run-dt", "data"),
    Input("tomogram-index", "data"),
    prevent_initial_call=True
)
def load_tomogram_run(tomogram_index):
    dt = defaultdict(list)
    if tomogram_index is not None:
        # takes 18s for VPN
        t1 = time.time()
        copick_dataset.load_curr_run(run_name=tomogram_index, sort_by_score=True)
        # takes 0.2s
        t2 = time.time()
        print('find copick run in copick', t2-t1)
        

    return dt


@callback(
    Output("image-slider", "value", allow_duplicate=True),
    Input("particle-dropdown", "value"),
    Input("display-row", "value"),
    Input("display-col", "value"),
    prevent_initial_call=True
)
def reset_slider(value, nrow, ncol):
    return 0


@callback(
    Output("output-image-upload", "children"),
    Output("particle-dropdown", "options"),
    Output("fig1", "figure"),
    Output("image-slider", "max"),
    Output("image-slider", "marks"),
    Output("crop-label", "children"),
    Output("image-slider", "value", allow_duplicate=True),
    Output("keybind-num", "data"),
    Input("tabs", "active_tab"),
    Input("image-slider", "value"),
    Input("crop-width", "value"),
    Input("crop-avg", "value"),
    Input("particle-dropdown", "value"),
    Input("accept-bttn", "n_clicks"),
    Input("reject-bttn", "n_clicks"),
    Input("assign-bttn", "n_clicks"),
    Input("username-analysis", "value"),
    Input("keybind-event-listener", "event"),
    Input("keybind-event-listener", "n_events"),
    Input("display-row", "value"),
    Input("display-col", "value"),
    State("tomogram-index", "data"),
    State("fig1", "figure"),
    State("output-image-upload", "children"),
    State("keybind-num", "data"),
    State({'type': 'thumbnail-image', 'index': ALL}, 'n_clicks'),
    State("assign-dropdown", "value"),
    prevent_initial_call=True
)
def update_analysis(
    at, 
    slider_value, 
    crop_width, 
    crop_avg, 
    particle, 
    accept_bttn, 
    reject_bttn, 
    assign_bttn, 
    copicklive_username,
    keybind_event_listener, 
    n_events,
    nrow,
    ncol,
    tomogram_index, 
    fig1, 
    fig2, 
    kbn, 
    thumbnail_image_select_value,
    new_particle
):
    pressed_key = None
    if ctx.triggered_id == "keybind-event-listener":
        #user is going to type in the class creation/edit modals and we don't want to trigger this callback using keys
        pressed_key = (
            keybind_event_listener.get("key", None) if keybind_event_listener else None
        )
        if not pressed_key:
            raise PreventUpdate
        else:
            print(f'pressed_key {pressed_key}')
    
    slider_max = 0
    changed_id = [p['prop_id'] for p in ctx.triggered][0]
    # takes 0.35s on mac3
    if tomogram_index:
        #time.sleep(7)
        #particle_dict = {k: k for k in sorted(set(copick_dataset.dt['pickable_object_name']))}
        if at == "tab-1":
            time.sleep(2)
            particle_dict = {k: k for k in sorted(set(copick_dataset.dt['pickable_object_name']))}
            df = pd.DataFrame.from_dict(copick_dataset.dt)
            fig1 = px.scatter_3d(df, x='x', y='y', z='z', color='pickable_object_name', symbol='user_id', size='size', opacity=0.5)
            return fig2, particle_dict, fig1, slider_max, {0: '0', slider_max: str(slider_max)}, no_update, no_update, no_update
        elif at == "tab-2":
            #new_particle = None
            if pressed_key in [str(i+1) for i in range(len(local_dataset._im_dataset['name']))]:
                new_particle = local_dataset._im_dataset['name'][int(pressed_key)-1]
            elif pressed_key == 's':
                new_particle = kbn

            copick_dataset.new_user_id(user_id=copicklive_username)
            if ("display-row" in changed_id or\
                "display-col" in changed_id) or \
                particle in copick_dataset.points_per_obj:
                if len(copick_dataset.points_per_obj[particle])%(nrow*ncol):
                    slider_max = len(copick_dataset.points_per_obj[particle])//(nrow*ncol)
                else:
                    slider_max = len(copick_dataset.points_per_obj[particle])//(nrow*ncol) - 1
                        
            positions = [i for i in range(slider_value*nrow*ncol, min((slider_value+1)*nrow*ncol, len(copick_dataset.points_per_obj[particle])))] 
            # loading zarr takes 6-8s for VPN
            particle_dict = {k: k for k in sorted(set(copick_dataset.dt['pickable_object_name']))}
            dim_z, dim_y, dim_x = copick_dataset.tomogram.shape
            msg = f"Image crop width (max {min(dim_x, dim_y)})"
            if crop_width is not None:
                half_width = crop_width//2
                if crop_avg is None:
                    crop_avg = 0
                fig2 = draw_gallery(run=tomogram_index, particle=particle, positions=positions, hw=half_width, avg=crop_avg, nrow=nrow, ncol=ncol)


            selected = [i for i,v in enumerate(thumbnail_image_select_value) if v%2 == 1]
            selected_point_ids = [positions[i] for i in selected]
            if 'accept-bttn' in changed_id or pressed_key=='a':
                copick_dataset.handle_accept_batch(selected_point_ids, particle)
            elif 'reject-bttn' in changed_id or pressed_key=='d':
                copick_dataset.handle_reject_batch(selected_point_ids, particle)
            elif 'assign-bttn' in changed_id or pressed_key=='s':
                copick_dataset.handle_assign_batch(selected_point_ids, particle, new_particle)

            # update figures
            # if 'accept-bttn' in changed_id or \
            #    'reject-bttn' in changed_id or \
            #    'assign-bttn' in changed_id or \
            #    pressed_key in ['a', 'd', 's']:
            #     slider_value += 1
            #     positions = [i for i in range(slider_value*nrow*ncol, min((slider_value+1)*nrow*ncol, len(copick_dataset.points_per_obj[particle])))] 
            #     fig2 = draw_gallery(run=tomogram_index, particle=particle, positions=positions, hw=half_width, avg=crop_avg, nrow=nrow, ncol=ncol)
            
            if 'assign-bttn' in changed_id or pressed_key == 's':
                positions = [i for i in range(slider_value*nrow*ncol, min((slider_value+1)*nrow*ncol, len(copick_dataset.points_per_obj[particle])))] 
                fig2 = draw_gallery(run=tomogram_index, particle=particle, positions=positions, hw=half_width, avg=crop_avg, nrow=nrow, ncol=ncol)    
            
            if pressed_key=='ArrowRight' and slider_value < slider_max:
                slider_value += 1
                positions = [i for i in range(slider_value*nrow*ncol, min((slider_value+1)*nrow*ncol, len(copick_dataset.points_per_obj[particle])))] 
                fig2 = draw_gallery(run=tomogram_index, particle=particle, positions=positions, hw=half_width, avg=crop_avg, nrow=nrow, ncol=ncol)
            elif pressed_key=='ArrowLeft' and slider_value:
                slider_value -= 1
                positions = [i for i in range(slider_value*nrow*ncol, min((slider_value+1)*nrow*ncol, len(copick_dataset.points_per_obj[particle])))] 
                fig2 = draw_gallery(run=tomogram_index, particle=particle, positions=positions, hw=half_width, avg=crop_avg, nrow=nrow, ncol=ncol)

            return fig2, particle_dict, blank_fig(), slider_max, {0: '0', slider_max: str(slider_max)}, msg, slider_value, new_particle
    else:
        return fig2, dict(), blank_fig(), slider_max, {0: '0', slider_max: str(slider_max)}, no_update, no_update, no_update




@callback(
    Output({'type': 'thumbnail-card', 'index': MATCH}, 'color'),
    Input({'type': 'thumbnail-image', 'index': MATCH}, 'n_clicks'),
    Input('select-all-bttn', 'n_clicks'),
    Input('unselect-all-bttn', 'n_clicks'),
    State("image-slider", "value"),
    State("display-row", "value"),
    State("display-col", "value"),
    State("particle-dropdown", "value"), 
    State({'type': 'thumbnail-image', 'index': MATCH}, 'id'), 
)
def select_thumbnail(value, 
                     select_clicks, 
                     unselect_clicks, 
                     slider_value, 
                     nrow, ncol, 
                     particle, 
                     comp_id):
    '''
    This callback assigns a color to thumbnail cards in the following scenarios:
        - An image has been selected, but no label has been assigned (blue)
        - An image has been labeled (label color)
        - An image has been unselected or unlabeled (no color)
    Args:
        value:                      Thumbnail card that triggered the callback (n_clicks)
    Returns:
        thumbnail_color:            Color of thumbnail card
    '''
    color = ''
    colors = ['', 'success', 'danger', 'warning']
    positions = [i for i in range(slider_value*nrow*ncol, min((slider_value+1)*nrow*ncol, len(copick_dataset.points_per_obj[particle])))]
    #print(f'positions {positions}')
    selected = [copick_dataset.picked_points_mask[copick_dataset.points_per_obj[particle][i][0]] for i in positions]
    #print(f'selected {selected}')
    #print(f'comp_id {comp_id}')
    color = colors[selected[int(comp_id['index'])]]
    #print(f'color {color} value {value}')
    if value is None or (ctx.triggered[0]['prop_id'] == 'unselect-all-bttn.n_clicks' and color==''):
        return ''
    if value % 2 == 1:
        return 'primary'
    else:
        return color


@callback(
    Output({'type': 'thumbnail-image', 'index': ALL}, 'n_clicks'),

    # Input({'type': 'label-button', 'index': ALL}, 'n_clicks_timestamp'),
    # Input('un-label', 'n_clicks'),
    Input('select-all-bttn', 'n_clicks'),
    Input('unselect-all-bttn', 'n_clicks'),

    State({'type': 'thumbnail-image', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def deselect(select_clicks, unselect_clicks, thumb_clicked):
    '''
    This callback deselects a thumbnail card
    Args:
        label_button_trigger:   Label button
        unlabel_n_clicks:       Un-label button
        unlabel_all:            Un-label all the images
        thumb_clicked:          Selected thumbnail card indice, e.g., [0,1,1,0,0,0]
    Returns:
        Modify the number of clicks for a specific thumbnail card
    '''
    # if all(x is None for x in label_button_trigger) and unlabel_n_clicks is None and unlabel_all is None:
    #     return [no_update]*len(thumb_clicked)
    if ctx.triggered[0]['prop_id'] == 'unselect-all-bttn.n_clicks':
        print([0 for thumb in thumb_clicked])
        return [0 for thumb in thumb_clicked]
    elif ctx.triggered[0]['prop_id'] == 'select-all-bttn.n_clicks':
        return [1 for thumb in thumb_clicked]





@callback(
    Output("download-json", "data"),
    Input("btn-download", "n_clicks"),
    State("username", "value"),
    prevent_initial_call=True,
)
def download_json(n_clicks, input_value):
    input_value = '.'.join(input_value.split(' '))
    filename = 'copick_config_' + '_'.join(input_value.split('.')) + '.json'   
    local_dataset.config_file["user_id"] = input_value
    return dict(content=json.dumps(local_dataset.config_file, indent=4), filename=filename)


@callback(
    Output("download-txt", "data"),
    Input("btn-download-txt", "n_clicks"),
    #State("username", "value"),
    prevent_initial_call=True,
)
def download_txt(n_clicks):
    print(f'COUNTER_FILE_PATH 0 {COUNTER_FILE_PATH}')
    if COUNTER_FILE_PATH:
        with open(COUNTER_FILE_PATH) as f:
            counter = json.load(f)
        
        if counter['repeat'] == 2:
            counter['start'] += counter['tasks_per_person']
            counter['repeat'] = 0

        counter['repeat'] += 1
        task_contents = '\n'.join(dirs[counter['start']:counter['start']+counter['tasks_per_person']])
        print(task_contents)
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
    data = local_dataset.fig_data()
    fig = px.bar(x=data['name'], 
                 y=data['count'], 
                 labels={'x': 'Objects', 'y':'Counts'}, 
                 text_auto=True,
                 color = data['name'],
                 color_discrete_map = data['colors'],
                 )
    fig.update(layout_showlegend=False)
    num_candidates = len(dirs) if len(dirs) < 100 else 100
    candidates = local_dataset.candidates(num_candidates, random_sampling=False)
    num_per_person_ordered = local_dataset.num_per_person_ordered 
    label = f'Labeled {len(local_dataset.tomos_pickers)} out of 1000 tomograms'
    bar_val = round(len(local_dataset.tomos_pickers)/1000*100, 1)
    
    return fig, \
           dbc.ListGroup([candidate_list(i, j) for i, j in candidates.items()], flush=True), \
           dbc.ListGroup([ranking_list(i, len(j)) for i, j in num_per_person_ordered.items()], numbered=True), \
           [label], \
           bar_val, \
           f'{bar_val}%'


@callback(
    Output('composition', 'children'),
    #Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_compositions(n):
    progress_list = []
    composition_list = html.Div()
    data = local_dataset.fig_data()
    l = 1/len(data['colors'])*100
    obj_order = {name:i for i,name in enumerate(data['name'])}
    tomograms = {k:v for k,v in sorted(local_dataset.tomograms.items(), key=lambda x: dir2id[x[0]])} 
    for tomogram,ps in tomograms.items():
        progress = []
        ps = [p for p in ps if p in obj_order]
        ps = sorted(list(ps), key=lambda x: obj_order[x])
        for p in ps:
            progress.append(dbc.Progress(value=l, color=data['colors'][p], bar=True))
        
        bttn = html.Button(id={"type": "tomogram-eval-bttn", "index": tomogram}, className="fa fa-search", style=roundbutton)
        progress_list.append(dbc.ListGroupItem(children=[dbc.Row([tomogram, bttn]), dbc.Progress(progress)], style={"border": 'transparent'}))
    
    composition_list = dbc.ListGroup(progress_list)
    return composition_list


