import plotly.express as px
import dash_bootstrap_components as dbc

from utils.data_utils import dataset
from dash import (
    Input,
    Output,
    callback,
)


def candidate_list(i, j):
    return  dbc.ListGroupItem("Test_{:03d} (labeled {} times)".format(i, j))

def ranking_list(i, j):
    return  dbc.ListGroupItem("{} {} tomograms".format(i, j))


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
    candidates = dataset.candidates(10) 
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

