import json
import plotly.express as px

with open('assets/copick_config_default.json') as f:
    config = json.load(f)

print(config["pickable_objects"])

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