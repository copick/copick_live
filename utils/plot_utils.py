import plotly.express as px
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