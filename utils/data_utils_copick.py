import os

import configparser
from copick.impl.filesystem import CopickRootFSSpec
from copick.models import CopickPoint, CopickLocation
from collections import defaultdict

import pandas as pd


config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"))
COPICKLIVE_CONFIG_PATH = '%s' % config['copicklive_config']['COPICKLIVE_CONFIG_PATH']

class CopickDataset:
    def __init__(self, config_path: str=None):
        self.root = CopickRootFSSpec.from_file(config_path) if config_path else None
        self.data = None
        self.current_point = None
        self.picks = None
        self.all_points = []  #[(x,y,z),...]
        self.point_types = []  #['ribosome',...]
        self.points_per_obj = defaultdict(list) # {'ribosome': [0,2,3...],...}
        self.picked_id_per_obj = defaultdict(list) # {'ribosome': [0,2,3...],...}
        self.picked_points_per_obj = defaultdict(list) # {'ribosome': [point_obj...],...}

        self.logs = defaultdict(list) # {'user_id':[], 'x': [], 'y':[], 'z':[], 'operation':['reject', 'accept', 'reassign'], 'start_class':[], 'end_class'[]}


    def load_local_tomogram_dataset(self, local_tomogram_dataset=None):
        if local_tomogram_dataset is not None:
            self.data = local_tomogram_dataset
            for pick in self.data.picks:
                if 'points' in pick:
                    points = pick['points']
                    for point in points:
                        self.points_per_obj[pick['pickable_object_name']].append(len(self.all_points))
                        self.point_types.append(pick['pickable_object_name']) 
                        self.all_points.append((point['location']['x'], \
                                                point['location']['y'], \
                                                point['location']['z']))

    
    def _store_points(self, obj_name=None, session_id='18'):
        if obj_name is not None:
            self.picks = self.run.get_picks(object_name=obj_name, user_id=self.root.user_id, session_id=session_id)
            if not self.picks:
                self.picks = self.run.new_picks(object_name=obj_name, user_id=self.root.user_id, session_id=session_id)
                self.picks = self.run.get_picks(object_name=obj_name, user_id=self.root.user_id, session_id=session_id)
            pick_set = self.picks[0]
            pick_set.points = self.picked_points_per_obj[obj_name]
            pick_set.store()

    
    
    def new_user_id(self, user_id=None):
        if user_id is not None:
            self.root.config.user_id = user_id

    
    def load_curr_run(self, run_name=None):
        self.run_name = run_name
        if self.run_name is not None:
            self.run =  self.root.get_run(self.run_name)
    

    def load_curr_point(self, point_id=None, obj_name=None):
        if point_id is not None and obj_name is not None:   
            self.pickable_obj_name = obj_name 
            print("Creating current pick point")
            self.current_point = self.points_per_obj[obj_name][point_id]   # current point index
            self.current_point_location = self.all_points[self.current_point]   

    
    def change_obj_name(self, obj_name=None, enable_log=True):
        if enable_log:
            self.log_operation(operation='reasign', old_obj_name=self.point_types[self.current_point], new_obj_name=obj_name)

        if obj_name is not None and self.current_point is not None:
            self.point_types[self.current_point] = obj_name
        
    
    
    def log_operation(self, operation=None, old_obj_name=None, new_obj_name=None):
        if os.path.exists('logs.csv') == False:
            self.logs['run_name'].append(self.run_name)
            self.logs['user_id'].append(self.root.config.user_id)
            self.logs['x'].append(self.current_point_location[0])
            self.logs['y'].append(self.current_point_location[1])
            self.logs['z'].append(self.current_point_location[2])
            self.logs['operation'].append('placeholder')
            self.logs['start_class'].append('NC')
            self.logs['end_class'].append('NC')
            pd.DataFrame(self.logs).to_csv('logs.csv', sep='\t', index=False)

        df = pd.read_csv('logs.csv', sep='\t')
        self.logs = df.to_dict('list') if len(df) else defaultdict(list) 
        #{'user_id':[], 'x': [], 'y':[], 'z':[], 'operation':['reject', 'accept', 'reassign'], 'start_class':[], 'end_class'[]}
        print(f'self.logs\n {self.logs}')
        if operation is not None and old_obj_name is not None and new_obj_name is not None:
            self.logs['run_name'].append(self.run_name)
            self.logs['user_id'].append(self.root.config.user_id)
            self.logs['x'].append(self.current_point_location[0])
            self.logs['y'].append(self.current_point_location[1])
            self.logs['z'].append(self.current_point_location[2])
            self.logs['operation'].append(operation)
            self.logs['start_class'].append(old_obj_name)
            self.logs['end_class'].append(new_obj_name)
        
            df = pd.DataFrame.from_dict(self.logs)
            df.to_csv('logs.csv', sep='\t', index=False)
    

    def handle_accept(self):
        if self.current_point is not None:
            obj_name = self.point_types[self.current_point]
            print(f"Accept, Object Type: {obj_name}, Run Name: {self.run_name}, Location: {self.current_point_location}")
            print(obj_name, self.picked_id_per_obj)
            self.point_types[self.current_point] = obj_name
            if self.current_point not in self.picked_id_per_obj[obj_name]:
                self.picked_id_per_obj[obj_name].append(self.current_point)
                self.picked_points_per_obj[obj_name].append(CopickPoint(location=CopickLocation(x=self.current_point_location[0], \
                                                                                                y=self.current_point_location[1], \
                                                                                                z=self.current_point_location[2])))
            self._store_points(obj_name)

    
    def handle_reject(self, enable_log=True):
        if enable_log:
            self.log_operation(operation='reject', old_obj_name='NC', new_obj_name='NC')

        if self.current_point is not None:
            try:
                obj_name =self.point_types[self.current_point]
                index = self.picked_id_per_obj[obj_name].index(self.current_point)
                print(f'reject point index {self.current_point}, index in the list {index}')
                self.picked_id_per_obj[obj_name].pop(index)
                self.picked_points_per_obj[obj_name].pop(index)
                self._store_points(obj_name)
            except:
                pass


    def handle_assign(self, new_bj_name=None):
        self.handle_reject(enable_log=False)
        self.change_obj_name(new_bj_name)
        self.handle_accept()



copick_dataset = CopickDataset(COPICKLIVE_CONFIG_PATH)
