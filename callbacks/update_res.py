import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import json
import pandas as pd
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from flask_caching import Cache
from app import app
import zarr, os
from functools import lru_cache 
from zarr.storage import LRUStoreCache, DirectoryStore

import numpy as np
from utils.data_utils_threading import (
    dataset, 
    dirs, 
    dir2id, 
    COUNTER_FILE_PATH, 
    TOMO_FILE_PATH, 
    TomogramDataset
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

def grid_inds(point, hw):
    x, y, z = point
    x //= 10
    y //= 10
    z //= 10
    x += hw
    y += hw
    z += hw
    return x, y, z


def crop_image2d(image, point, hw):
    x, y, z = grid_inds(point, hw)
    return image[int(x)-hw:int(x)+hw+1, int(y)-hw:int(y)+hw+1, int(z)]

def crop_image3d(image, point, hw):
    x, y, z = grid_inds(point, hw)
    return image[int(x)-hw:int(x)+hw+1, int(y)-hw:int(y)+hw+1, int(z)-hw:int(z)+hw+1]


@lru_cache(maxsize=128)  # number of images
def prepare_images2d(run, bin=0, hw=30):
    data = TomogramDataset(run)
    padded_image = np.pad(data.tomogram, ((hw,hw), (hw,hw), (hw, hw)), 'constant')
    dt = defaultdict(set)
    for pick in data.picks:
        try:
            points = pick['points']
            for point in points:
                dt[pick['pickable_object_name']].add((point['location']['x'], \
                                                      point['location']['y'], \
                                                      point['location']['z'])) 
        except:
            pass
    
    
    os.makedirs("./cache-directory", exist_ok=True)
    # Create an LRU cache for the store with a maximum size of 100 MB
    store = DirectoryStore(f'./cache-directory/{run}_2d_crops.zarr')
    cache_store = LRUStoreCache(store, max_size=100 * 2**20)
    root = zarr.group(store=store, overwrite=False)

    
    cropped_images_groups = {}
    points_groups = defaultdict(list)
    for particle, points in dt.items():
        cropped_images = []
        points_list = []
        for p in points:
            cropped_image = crop_image2d(padded_image, p, hw)
            cropped_images.append(cropped_image)
            points_list.append(p)

        cropped_images = np.array(cropped_images)
        print(cropped_images.shape)
        # if particle not in root:
        #     root.create_dataset(particle, data=cropped_images)
        # else:
        #     root[particle][:] = cropped_images
        cropped_images_groups[particle] = cropped_images
        points_groups[particle] = points_list
        
    return cropped_images_groups,  points_groups 
    


@lru_cache(maxsize=8)  # number of images
def prepare_images3d(run, bin=0, hw=15):
    data = TomogramDataset(run)
    padded_image = np.pad(data.tomogram, ((hw,hw), (hw,hw), (hw, hw)), 'constant')
    dt = defaultdict(set)
    for pick in data.picks:
        try:
            points = pick['points']
            for point in points:
                dt[pick['pickable_object_name']].add((point['location']['x'], \
                                                      point['location']['y'], \
                                                      point['location']['z'])) 
        except:
            pass
    
    
    os.makedirs("./cache-directory", exist_ok=True)
    # Create an LRU cache for the store with a maximum size of 100 MB
    store = DirectoryStore(f'./cache-directory/{run}_3d_crops.zarr')
    cache_store = LRUStoreCache(store, max_size=100 * 2**20)
    root = zarr.group(store=store, overwrite=False)

    
    cropped_images_groups = {}
    points_groups = defaultdict(list)
    for particle, points in dt.items():
        cropped_images = []
        points_list = []
        for p in points:
            cropped_image = crop_image3d(padded_image, p, hw)
            cropped_images.append(cropped_image)
            points_list.append(p)

        cropped_images = np.array(cropped_images)
        print(cropped_images.shape)
        # if particle not in root:
        #     root.create_dataset(particle, data=cropped_images)
        # else:
        #     root[particle][:] = cropped_images
        cropped_images_groups[particle] = cropped_images
        points_groups[particle] = points_list
        
    return cropped_images_groups,  points_groups 



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
    Output("modal-evaluation", "is_open"),
    Output("collapse1", "is_open"),
    Output("collapse2", "is_open"),
    Output("fig1", "figure"),
    Output("fig2", "figure"),
    Output("image-slider", "max"),
    Output("image-slider", "marks"),
    Input("tabs", "active_tab"),
    Input("tomogram-index", "data"),
    Input("image-slider", "value"),
    State("modal-evaluation", "is_open"),
    State("fig1", "figure"),
    State("fig2", "figure"),
    prevent_initial_call=True
)
def toggle_3dplot_modal(at, tomogram_index, slider_value, is_open, fig1, fig2):
    slider_max = 10
    if tomogram_index:
        if at == "tab-1":
            dt = defaultdict(list)
            for pick in TomogramDataset(tomogram_index).picks:
                try:
                    points = pick['points']
                    for point in points:
                        dt['pickable_object_name'].append(pick['pickable_object_name'])
                        dt['user_id'].append(pick['user_id'])
                        dt['x'].append(point['location']['x']/10)
                        dt['y'].append(point['location']['y']/10)
                        dt['z'].append(point['location']['z']/10)
                        dt['size'].append(0.1)
                except:
                    pass
            
            #assert len(df) != 0, "Dataframe is empty. Please check the data." 
            df = pd.DataFrame.from_dict(dt)
            print(fig1)
            # fig1.add_trace(go.Scatter3d(
            #     x=df['x'], 
            #     y=df['y'], 
            #     z=df['t'],
            #     marker=dict(
            #         color=df['pickable_object_name'],
            #         symbol=df['user_id'],
            #         size=df['size'],
            #     ),
            #     opacity=0.5
            #     ))
            fig1 = px.scatter_3d(df, x='x', y='y', z='z', color='pickable_object_name', symbol='user_id', size='size', opacity=0.5)
            return True, True, False, fig1,  blank_fig(), slider_max, {0: '0', slider_max: str(slider_max)}
        elif at == "tab-2":
            #print(f'slider_value {slider_value}')
            cropped_image, points = prepare_images2d(tomogram_index)
            #print(points['ribosome'])
            fig2d = px.imshow(cropped_image['ribosome'][slider_value], binary_string=True)
            slider_max = len(cropped_image['ribosome'])
            fig2d.add_shape(type="circle",
                xref="x", yref="y",
                fillcolor="PaleTurquoise",
                x0=29, y0=31, x1=31, y1=29,
                line_color="LightSeaGreen",
            )
            fig2d.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
            fig2d.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
            return True, False, True, blank_fig(), fig2d, slider_max, {0: '0', slider_max: str(slider_max)}
        elif at == "tab-3":
            X, Y, Z = np.mgrid[0:1:31j, 0:1:31j, 0:1:31j]
            cropped_volume, points = prepare_images3d(tomogram_index)
            # fig3d = go.Figure(data=go.Volume(
            #     x=X.flatten(),
            #     y=Y.flatten(),
            #     z=Z.flatten(),
            #     value=cropped_volume['ribosome'][0].flatten(),
            #     isomin=0,
            #     isomax=1,
            #     opacity=0.2, # needs to be small to see through all surfaces
            #     surface_count=300, # needs to be a large number for good volume rendering
            #     colorscale='gray',
            #     ))
            fig3d = go.Figure()
            fig3d.add_trace(go.Isosurface(
                                        x=X.flatten(),
                                        y=Y.flatten(),
                                        z=Z.flatten(), 
                                        value=cropped_volume['ribosome'][0].flatten(),
                                        isomin=0,
                                        isomax=1,
                                        opacity=0.2,
                                        surface_count=1000, # needs to be a large number for good volume rendering
                                        colorscale='gray',
                                        ))
            # fig3d.add_shape(type="circle",
            #     xref="x", yref="y", zref="z",
            #     fillcolor="PaleTurquoise",
            #     x0=29, y0=31, z0=30, x1=31, y1=29, z1=30,
            #     line_color="LightSeaGreen",
            # )
            # fig3d.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
            # fig3d.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
            # fig3d.update_zaxes(showgrid=False, showticklabels=False, zeroline=False)

            return True, False, True,  blank_fig(),  fig3d, slider_max, {0: '0', slider_max: str(slider_max)}
    else:
        return False, False, False,  blank_fig(),  blank_fig(), slider_max, {0: '0', slider_max: str(slider_max)}



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


