import json
import plotly.express as px
from utils.data_utils_threading import COPICK_CONFIG_PATH

with open(COPICK_CONFIG_PATH) as f:
    config = json.load(f)


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