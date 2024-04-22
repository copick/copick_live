#from utils.data_utils import Dataset
from dash import (
    Input,
    Output,
    callback,
)
import plotly.express as px
import dash_bootstrap_components as dbc


dataset = [
    {'candidates': [5, 7, 9, 22, 37, 59, 56, 89, 77], 
     'times':[1, 1, 0, 0 , 0 , 0, 0 , 0, 0], 
     'num_per_person_ordered': {'Phil': 8, 'John.Doe':7, 'Tom':5, 'Julie':3, 'Jay':1},
     'data': {'apoF': 3, 'amlayse': 4, 'beta-gal': 5, 'ribosome': 10, 'THG':2, 'VLP':1},
     'counts': 100
     }, 
     {'candidates': [9, 22, 37, 59, 56, 66, 89, 77, 98], 
     'times':[0, 0, 0, 0, 0, 0, 0, 0, 0], 
     'num_per_person_ordered': {'John.Doe':9, 'Phil': 8, 'Tom':5, 'Julie':3, 'Jay':2},
     'data': {'apoF': 5, 'amlayse': 7, 'beta-gal': 5, 'ribosome': 37, 'THG':2, 'VLP':1},
     'counts': 130
     }, 
     {'candidates': [137, 159, 56, 189, 177, 88, 107, 69, 183], 
     'times':[1, 1, 1 , 0, 0, 0 , 0, 0, 0], 
     'num_per_person_ordered': {'Julie':20, 'jennifer': 13, 'John.Doe':9, 'Phil': 8, 'Tom':7, 'Jay':2},
     'data': {'apoF': 11, 'amlayse': 14, 'beta-gal': 25, 'ribosome': 70, 'THG':6, 'VLP':5},
     'counts': 235
     },
     {'candidates': [189, 177, 88, 107, 69, 183, 399, 274, 981], 
     'times':[1, 1, 0, 0 , 0, 0 , 0, 0, 0], 
     'num_per_person_ordered': {'Julie':22, 'jennifer': 13, 'John.Doe':10, 'Phil': 8, 'Tom':7, 'Jay':5},
     'data': {'apoF': 101, 'amlayse': 104, 'beta-gal': 25, 'ribosome': 170, 'THG':56, 'VLP':15},
     'counts': 385
     }
]



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
    m = n%4
    data = dataset[m]['data']
    fig = px.bar(x=data.keys(), y=data.values(), labels={'x': '', 'y':'count'}, text_auto='.2s')
    
    candidates = dataset[m]['candidates']
    times = dataset[m]['times']

    def item(i, j):
        return  dbc.ListGroupItem("Test_{:03d} (labeled {} times)".format(i, j))
    
    num_per_person_ordered = dataset[m]['num_per_person_ordered']
    label = f'Labeled {dataset[m]["counts"]} out of 1000 tomograms'
    bar_val = dataset[m]['counts']/1000*100

    def item2(i, j):
        return  dbc.ListGroupItem("{} {} tomograms".format(i, j))
    
    return fig, \
           dbc.ListGroup([item(i, j) for i, j in zip(candidates, times)], flush=True), \
           dbc.ListGroup([item2(i, j) for i, j in num_per_person_ordered.items()], numbered=True), \
           [label], \
           bar_val, \
           f'{bar_val}%'

