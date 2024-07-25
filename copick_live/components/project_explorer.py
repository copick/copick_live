import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from copick_live.utils.copick_dataset import get_copick_dataset
import json

def layout():
    return html.Div([
        dbc.Button("Load Project Structure", id="load-project-button", color="primary", className="mb-3"),
        html.Div(id="project-structure-container"),
        dcc.Store(id="project-structure-store", data={}),
    ])

@callback(
    Output("project-structure-container", "children"),
    Output("project-structure-store", "data"),
    Input("load-project-button", "n_clicks"),
    State("project-structure-store", "data"),
    prevent_initial_call=True
)
def load_project_structure(n_clicks, stored_data):
    if n_clicks is None:
        raise PreventUpdate

    copick_dataset = get_copick_dataset()
    project_structure = {"name": "Root", "children": []}

    for run in copick_dataset.root.runs:
        run_structure = {"name": run.name, "children": [
            {"name": "Picks", "children": [], "parent_run": run.name},
            {"name": "Segmentations", "children": [], "parent_run": run.name},
            {"name": "VoxelSpacing", "children": [], "parent_run": run.name}
        ]}
        project_structure["children"].append(run_structure)

    return render_structure(project_structure), project_structure

@callback(
    Output({"type": "expand-container", "index": ALL}, "children"),
    Input({"type": "expand-button", "index": ALL}, "n_clicks"),
    State({"type": "expand-container", "index": ALL}, "id"),
    State("project-structure-store", "data"),
    prevent_initial_call=True
)
def expand_node(n_clicks, container_ids, stored_data):
    if not n_clicks or not any(n_clicks):
        raise PreventUpdate

    triggered_id = json.loads(dash.callback_context.triggered[0]['prop_id'].split('.')[0])
    index_path = triggered_id['index']

    node = stored_data
    for idx in index_path.split(','):
        node = node['children'][int(idx)]

    if 'loaded' not in node:
        node['loaded'] = True
        copick_dataset = get_copick_dataset()
        
        if node['name'] == 'Picks':
            # Load picks data
            run_name = node['parent_run']
            copick_dataset.load_curr_run(run_name=run_name)
            for obj_name, points in copick_dataset.points_per_obj.items():
                node['children'].append({"name": f"{obj_name} ({len(points)})", "children": []})
        
        elif node['name'] == 'Segmentations':
            # Load segmentations data
            run_name = node['parent_run']
            run = copick_dataset.root.get_run(run_name)
            segmentations = run.get_segmentations()
            for seg in segmentations:
                node['children'].append({"name": seg.name, "children": []})
        
        elif node['name'] == 'VoxelSpacing':
            # Load voxel spacing data
            run_name = node['parent_run']
            run = copick_dataset.root.get_run(run_name)
            voxel_spacings = run.get_voxel_spacings()
            for vs in voxel_spacings:
                node['children'].append({"name": f"Spacing: {vs.spacing}", "children": [
                    {"name": f"Tomogram: {vs.get_tomogram().name}", "children": []},
                    {"name": f"CTF: {vs.get_ctf().name}", "children": []}
                ]})

    return [render_structure(node) if id['index'] == index_path else dash.no_update for id in container_ids]

def render_structure(node, path=''):
    children = []
    for i, child in enumerate(node.get('children', [])):
        new_path = f"{path},{i}" if path else str(i)
        expand_button = dbc.Button(
            "▶",
            id={"type": "expand-button", "index": new_path},
            size="sm",
            className="mr-2"
        ) if child.get('children') else None
        
        children.append(html.Div([
            expand_button,
            child['name'],
            html.Div(id={"type": "expand-container", "index": new_path}, style={'margin-left': '20px'})
        ]))
    return children
