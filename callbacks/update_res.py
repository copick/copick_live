import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import json, time
import pandas as pd
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler
import zarr, os
from functools import lru_cache 
from zarr.storage import LRUStoreCache, DirectoryStore

import time

import numpy as np
from utils.copick_dataset import copick_dataset
from utils.local_dataset import (
    dataset, 
    dirs, 
    dir2id, 
    COUNTER_FILE_PATH, 
    CACHE_ROOT,
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



# 1st update of the internal states
dataset.refresh()

#Scheduler
scheduler = BackgroundScheduler() # in-memory job stores
scheduler.add_job(func=dataset.refresh, trigger='interval', seconds=20)  # interval should be larger than the time it takes to refresh, o.w. it will be report incomplete stats.
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


def blank_fig():
    """
    Creates a blank figure with no axes, grid, or background.
    """
    fig = go.Figure()
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


def candidate_list(i, j):
    return  dbc.ListGroupItem("{} (labeled by {} person)".format(dirs[i], j))

def ranking_list(i, j):
    return  dbc.ListGroupItem("{} {} tomograms".format(i, j))



#====================================== memoization ======================================
# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# })

# TIMEOUT = 60


# @cache.memoize(timeout=TIMEOUT)
# def prepare_images(run, bin=0):
#     zarr_file_path = TOMO_FILE_PATH + run + '/VoxelSpacing10.000/denoised.zarr'
#     image = zarr.open(zarr_file_path, 'r')
#     return json.dumps(image[bin][:])


# def load_images(run: str):
#     return json.loads(prepare_images(run))


# def clear_cache():
#     cache.clear()

def grid_inds(copick_loc, hw):
    x, y, z = copick_loc.x, copick_loc.y, copick_loc.z
    x //= 10
    y //= 10
    z //= 10
    x += hw
    y += hw
    z += hw
    return x, y, z


def crop_image2d(image, copick_loc, hw, avg):
    x, y, z = grid_inds(copick_loc, hw)
    z_minus = max(int(z)-avg, hw)
    z_plus = min(int(z)+avg+1, image.shape[0]-hw)
    return np.mean(image[z_minus:z_plus, int(y)-hw:int(y)+hw+1, int(x)-hw:int(x)+hw+1], axis=0)  # (z, y, x) for copick coordinates

def crop_image3d(image, copick_loc, hw):
    x, y, z = grid_inds(copick_loc, hw)
    return image[int(z)-hw:int(z)+hw+1, int(y)-hw:int(y)+hw+1, int(x)-hw:int(x)+hw+1]


@lru_cache(maxsize=128)  # number of images
def prepare_images2d(run, bin=0, hw=60, avg=2):
    padded_image = np.pad(copick_dataset.tomogram, ((hw,hw), (hw,hw), (hw, hw)), 'constant')    
    # cache_dir = CACHE_ROOT + 'cache-directory/'
    # os.makedirs(cache_dir, exist_ok=True)
    # # Create an LRU cache for the store with a maximum size of 100 MB
    # store = DirectoryStore(f'{cache_dir}{run}_2d_crops.zarr')
    # #cache_store = LRUStoreCache(store, max_size=100 * 2**20)
    # root = zarr.group(store=store, overwrite=True)
    cropped_images_groups = {}
    for particle, ids in copick_dataset._points_per_obj.items():
        cropped_images = []
        for id in ids:
            cropped_image = crop_image2d(padded_image, copick_dataset._all_points[id].location, hw, avg)
            cropped_images.append(cropped_image)

        cropped_images = np.array(cropped_images)
        cropped_images_groups[particle] = cropped_images
        
    return cropped_images_groups
    


@lru_cache(maxsize=8)  # number of images
def prepare_images3d(run, bin=0, hw=15):
    padded_image = np.pad(copick_dataset.tomogram, ((hw,hw), (hw,hw), (hw, hw)), 'constant')
    # cache_dir = CACHE_ROOT + 'cache-directory/'
    # os.makedirs(cache_dir, exist_ok=True)
    # # Create an LRU cache for the store with a maximum size of 100 MB
    # store = DirectoryStore(f'{cache_dir}{run}_3d_crops.zarr')
    # cache_store = LRUStoreCache(store, max_size=100 * 2**20)
    # root = zarr.group(store=store, overwrite=False)
    cropped_images_groups = {}
    for particle, ids in copick_dataset._points_per_obj.items():
        cropped_images = []
        for id in ids:
            cropped_image = crop_image3d(padded_image, copick_dataset._all_points[id].location, hw)
            cropped_images.append(cropped_image)

        cropped_images = np.array(cropped_images)
        cropped_images_groups[particle] = cropped_images
        
    return cropped_images_groups



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
    Output("fig2", "figure", allow_duplicate=True),
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
        return blank_fig(), 0, None, True, "tab-1", msg
    else:
        return  blank_fig(), 0, None, False, "tab-1", msg


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
        copick_dataset.load_curr_run(run_name=tomogram_index)
        # takes 0.2s
        t2 = time.time()
        print('find copick run in copick', t2-t1)
        

    return dt


@callback(
    Output("image-slider", "value", allow_duplicate=True),
    Input("particle-dropdown", "value"),
    prevent_initial_call=True
)
def reset_slider(value):
    return 0


@callback(
    Output("particle-dropdown", "options"),
    Output("fig1", "figure"),
    Output("fig2", "figure"),
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
    State("tomogram-index", "data"),
    State("fig1", "figure"),
    State("fig2", "figure"),
    #State("assign-dropdown", "value"),
    State("run-dt", "data"),
    State("keybind-num", "data"),
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
    tomogram_index, 
    fig1, 
    fig2, 
    #new_particle, 
    dt,
    kbn
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
    
    slider_max = 10
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
            return particle_dict, fig1,  blank_fig(), slider_max, {0: '0', slider_max: str(slider_max)}, no_update, no_update, no_update
        elif at == "tab-2":
            new_particle = None
            if pressed_key in [str(i+1) for i in range(len(dataset._im_dataset['name']))]:
                new_particle = dataset._im_dataset['name'][int(pressed_key)-1]
            elif pressed_key == 's':
                new_particle = kbn

            
            copick_dataset.new_user_id(user_id=copicklive_username)
            # loading zarr takes 6-8s for VPN
            particle_dict = {k: k for k in sorted(set(copick_dataset.dt['pickable_object_name']))}
            dim_z, dim_y, dim_x = copick_dataset.tomogram.shape
            msg = f"Image crop width (max {min(dim_x, dim_y)})"
            print(msg)
            fig2 = blank_fig()
            if crop_width is not None:
                half_width = crop_width//2
                if crop_avg is None:
                    crop_avg = 0
                cropped_image = prepare_images2d(tomogram_index, bin=0, hw=half_width, avg=crop_avg)
                if particle in cropped_image:
                    fig2 = px.imshow(cropped_image[particle][slider_value], binary_string=True)
                    slider_max = len(cropped_image[particle])-1
                    fig2.add_shape(type="circle",
                        xref="x", yref="y",
                        fillcolor="PaleTurquoise",
                        x0=half_width-1, y0=half_width+1, x1=half_width+1, y1=half_width-1,
                        line_color="LightSeaGreen",
                    )
                    fig2.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
                    fig2.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

            #pressed_key  = ''
            copick_dataset.load_curr_point(point_id=slider_value, obj_name=particle)
            if 'accept-bttn' in changed_id or pressed_key=='a':
                copick_dataset.handle_accept()
            elif 'reject-bttn' in changed_id or pressed_key=='d':
                copick_dataset.handle_reject()
            elif 'assign-bttn' in changed_id or pressed_key=='s':
                copick_dataset.handle_assign(new_particle)

            if 'accept-bttn' in changed_id or \
               'reject-bttn' in changed_id or \
               'assign-bttn' in changed_id or \
               pressed_key in ['a', 'd', 's']:
                slider_value += 1
                fig2 = px.imshow(cropped_image[particle][slider_value], binary_string=True)
                fig2.add_shape(type="circle",
                    xref="x", yref="y",
                    fillcolor="PaleTurquoise",
                    x0=half_width-1, y0=half_width+1, x1=half_width+1, y1=half_width-1,
                    line_color="LightSeaGreen",
                )
                fig2.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
                fig2.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
            
            if pressed_key=='ArrowRight':
                slider_value += 1
                fig2 = px.imshow(cropped_image[particle][slider_value], binary_string=True)
                fig2.add_shape(type="circle",
                    xref="x", yref="y",
                    fillcolor="PaleTurquoise",
                    x0=half_width-1, y0=half_width+1, x1=half_width+1, y1=half_width-1,
                    line_color="LightSeaGreen",
                )
                fig2.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
                fig2.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
            elif pressed_key=='ArrowLeft':
                slider_value -= 1
                fig2 = px.imshow(cropped_image[particle][slider_value], binary_string=True)
                fig2.add_shape(type="circle",
                    xref="x", yref="y",
                    fillcolor="PaleTurquoise",
                    x0=half_width-1, y0=half_width+1, x1=half_width+1, y1=half_width-1,
                    line_color="LightSeaGreen",
                )
                fig2.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
                fig2.update_yaxes(showgrid=False, showticklabels=False, zeroline=False) 

            return particle_dict, blank_fig(), fig2, slider_max, {0: '0', slider_max: str(slider_max)}, msg, slider_value, new_particle
        # elif at == "tab-3":
        #     X, Y, Z = np.mgrid[0:1:31j, 0:1:31j, 0:1:31j]
        #     cropped_volume, points = prepare_images3d(tomogram_index)
        #     # fig3d = go.Figure(data=go.Volume(
        #     #     x=X.flatten(),
        #     #     y=Y.flatten(),
        #     #     z=Z.flatten(),
        #     #     value=cropped_volume['ribosome'][0].flatten(),
        #     #     isomin=0,
        #     #     isomax=1,
        #     #     opacity=0.2, # needs to be small to see through all surfaces
        #     #     surface_count=300, # needs to be a large number for good volume rendering
        #     #     colorscale='gray',
        #     #     ))
        #     fig3d = go.Figure()
        #     fig3d.add_trace(go.Isosurface(
        #                                 x=X.flatten(),
        #                                 y=Y.flatten(),
        #                                 z=Z.flatten(), 
        #                                 value=cropped_volume['ribosome'][0].flatten(),
        #                                 isomin=0,
        #                                 isomax=1,
        #                                 opacity=0.2,
        #                                 surface_count=1000, # needs to be a large number for good volume rendering
        #                                 colorscale='gray',
        #                                 reversescale=True
        #                                 ))
        #     # fig3d.add_shape(type="circle",
        #     #     xref="x", yref="y", zref="z",
        #     #     fillcolor="PaleTurquoise",
        #     #     x0=29, y0=31, z0=30, x1=31, y1=29, z1=30,
        #     #     line_color="LightSeaGreen",
        #     # )
        #     # fig3d.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
        #     # fig3d.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
        #     # fig3d.update_zaxes(showgrid=False, showticklabels=False, zeroline=False)

        #     return True, False, True,  blank_fig(),  fig3d, slider_max, {0: '0', slider_max: str(slider_max)}
    else:
        return dict(), blank_fig(),  blank_fig(), slider_max, {0: '0', slider_max: str(slider_max)}, no_update, no_update, no_update



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
    num_candidates = len(dirs) if len(dirs) < 100 else 100
    candidates = dataset.candidates(num_candidates, random_sampling=False)
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
    #Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_compositions(n):
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
        
        bttn = html.Button(id={"type": "tomogram-eval-bttn", "index": tomogram}, className="fa fa-search", style=roundbutton)
        progress_list.append(dbc.ListGroupItem(children=[dbc.Row([tomogram, bttn]), dbc.Progress(progress)], style={"border": 'transparent'}))
    
    composition_list = dbc.ListGroup(progress_list)
    return composition_list


