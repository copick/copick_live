import dash_bootstrap_components as dbc
from dash import html
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
import io
import base64
import numpy as np

from utils.copick_dataset import get_copick_dataset
from functools import lru_cache 



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
    out = np.mean(image[z_minus:z_plus, int(y)-hw:int(y)+hw+1, int(x)-hw:int(x)+hw+1], axis=0)  # (z, y, x) for copick coordinates
    return np.swapaxes(out, 1, 0)  # change back to (z, x, y) for plotting, in accordance with ChimeraX after 90 deg clockwise rotation.


#====================================== memoization ======================================
#@lru_cache(maxsize=128)  # number of images
def prepare_images2d(run=None, particle=None, positions=[], hw=60, avg=2):
    padded_image = np.pad(get_copick_dataset().tomogram, ((hw,hw), (hw,hw), (hw, hw)), 'constant')    
    # cache_dir = CACHE_ROOT + 'cache-directory/'
    # os.makedirs(cache_dir, exist_ok=True)
    # # Create an LRU cache for the store with a maximum size of 100 MB
    # store = DirectoryStore(f'{cache_dir}{run}_2d_crops.zarr')
    # #cache_store = LRUStoreCache(store, max_size=100 * 2**20)
    # root = zarr.group(store=store, overwrite=True)
    cropped_image_batch = []
    if particle in get_copick_dataset().points_per_obj and len(positions):
        point_ids = [get_copick_dataset().points_per_obj[particle][i][0] for i in positions]
        point_objs = [get_copick_dataset().all_points[id] for id in point_ids]
        for point_obj in point_objs:
            cropped_image = crop_image2d(padded_image, point_obj.location, hw, avg)
            cropped_image_batch.append(cropped_image)
        
    return np.array(cropped_image_batch)



def blank_fig():
    """
    Creates a blank figure with no axes, grid, or background.
    """
    fig = go.Figure()
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig



def barplot(x, y, xlabel=None, ylabel=None, colors: bool | list=None):
    if colors:
        fig = px.bar(x=x, 
                    y=y, 
                    labels={'x': xlabel, 'y':ylabel}, 
                    text_auto=True,
                    color = colors,
                    )
        fig.update(layout_showlegend=False)
    return fig


def plot_crop_image(arr, hw):
    fig = px.imshow(arr, binary_string=True) 
    fig.add_shape(type="circle",
        xref="x", yref="y",
        fillcolor="PaleTurquoise",
        x0=hw-1, y0=hw+1, x1=hw+1, y1=hw-1,
        line_color="LightSeaGreen",
    )
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


def plot3d(x, y):
    pass    


def arr2base64(image_array):
    min_val = np.min(image_array)
    max_val = np.max(image_array)
    normalized_array = (image_array - min_val) / (max_val - min_val)

    # Convert the normalized array to the RGB range [0, 255]
    rgb_array = (normalized_array * 255).astype('uint8')
    
    # Convert the image array to a PIL Image object
    image = Image.fromarray(rgb_array)

    # Save the image to a bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()

    # Encode the bytes in base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_base64



def image_card(image_arr, index=0):
    image = html.Div(
        children=[dbc.Card(
                    id={'type': 'thumbnail-card', 'index': index},
                    children=[
                            html.A(id={'type': 'thumbnail-image', 'index': index},
                                n_clicks=0,   
                                children=dbc.CardImg(id={'type': 'thumbnail-src', 'index': index},
                                                        src=f'data:image/png;base64,{arr2base64(image_arr)}',
                                                        bottom=False)),
                                #dbc.CardBody([html.P(style={'whiteSpace': 'pre-wrap', 'font-size': '12px'})])
                            ],
                    outline=False,
                    color='white',
                    style={"padding": "5%", "margin-bottom": "-10px", "margin-right": "-15px"})],

        id={'type': 'thumbnail-wrapper', 'index': index},
        style={'display': 'block'}
    )
    return image


def draw_gallery_components(list_of_image_arr, n_rows, n_cols):
    '''
    This function display the images per page
    Args:
        list_of_image_arr:   List of image arrays
        n_rows:             Number of rows
        n_cols:             Number of columns
    Returns:
        reactivate image components
    '''
    n_images = len(list_of_image_arr)
    n_cols = n_cols
    children = []
    for j in range(n_rows):
        row_child = []
        for i in range(n_cols):
            index = j * n_cols + i
            if index >= n_images:
                # no more images, on hanging row
                break
            curr_image_arr = list_of_image_arr[index]
            row_child.append(dbc.Col(image_card(curr_image_arr, j * n_cols + i), width="{}".format(12 // n_cols)))
        children.append(dbc.Row(row_child))
    return children


def draw_gallery(run=None, particle=None, positions=[], hw=60, avg=2, nrow=5, ncol=4):
    figures = []
    cropped_image_batch = prepare_images2d(run=run, particle=particle, positions=positions, hw=hw, avg=avg)
    if len(cropped_image_batch):
        figures = draw_gallery_components(cropped_image_batch, nrow, ncol)
    return figures
