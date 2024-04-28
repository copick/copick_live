import json
import plotly.express as px


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