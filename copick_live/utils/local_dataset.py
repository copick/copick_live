import os, time
from copick_live.config import get_config
from copick.impl.filesystem import CopickRootFSSpec
import random, copy
from collections import defaultdict, deque
import json
import concurrent

class LocalDataset:
    def __init__(self):
        config = get_config()
        self.root = CopickRootFSSpec.from_file(config.copick_config_path)
        self.counter_file_path = config.counter_file_path
        
        # output
        self.proteins = defaultdict(int) # {'ribosome': 38, ...}
        self.tomograms = defaultdict(set)  #{'TS_1_1':{'ribosome', ...}, ...}
        self.tomos_per_person = defaultdict(set) #{'john.doe':{'TS_1_1',...},...} 
        self.tomos_pickers = defaultdict(set)   #{'Test_1_1': {john.doe,...}, ...}
        self.num_per_person_ordered = dict() # {'Tom':5, 'Julie':3, ...}
        
        # hidden variables for updating candidate recommendations 
        self._all = set()
        self._tomos_done = set()   # labeled at least by 2 people
        self._tomos_one_pick = set() # labeled only by 1 person
        self._candidate_dict = defaultdict() # {1:1, 2:0, ...}
        self._prepicks = set(['slab-picking', 
                             'pytom-template-match', 
                             'relion-refinement', 
                             'prepick', 
                             'ArtiaX', 
                             'default']
                            ) 

        xdata = []
        colors = dict()
        for po in config.get("pickable_objects", []):
            xdata.append(po["name"])
            colors[po["name"]] = po["color"]

        self._im_dataset = {'name': xdata, 
                           'count': [], 
                           'colors': colors
                          }

    def _reset(self):
        self.proteins = defaultdict(int) 
        self._tomos_one_pick = set() #may remove some elems, therefore, empty before each check

        config = get_config()
        xdata = []
        colors = dict()
        for po in config.get("pickable_objects", []):
            xdata.append(po["name"])
            colors[po["name"]] = po["color"]
            
        self._im_dataset = {'name': xdata, 
                           'count': [], 
                           'colors': colors
                          }
        
    
    def refresh(self):
        self._reset()
        self._update_tomo_sts()

    
    def _process_run(self, run):
        for pick_set in run.get_picks():
            try:
                pickable_object_name = pick_set.pickable_object_name
                user_id = pick_set.user_id
                run_name = run.name
                points = pick_set.points

                if user_id not in self._prepicks and points and len(points):
                    self.proteins[pickable_object_name] += len(points)
                    self.tomos_per_person[user_id].add(run_name)
                    self.tomograms[run_name].add(pickable_object_name)
                    self.tomos_pickers[run_name].add(user_id)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for pick set in run {run.name}")
            except Exception as e:
                print(f"Unexpected error processing run {run.name}: {e}")

    def _update_tomo_sts(self):
        start = time.time() 
        runs = self.root.runs
        self._all = set(range(len(runs)))
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._process_run, runs)
        
        print(f'{time.time()-start} s to check all files')
        
        for tomo, pickers in self.tomos_pickers.items():
            run_id = next((i for i, run in enumerate(runs) if run.name == tomo), None)
            if run_id is not None:
                if len(pickers) >= 2:
                    self._tomos_done.add(run_id)
                elif len(pickers) == 1:
                    self._tomos_one_pick.add(run_id)

        self.num_per_person_ordered = dict(sorted(self.tomos_per_person.items(), key=lambda item: len(item[1]), reverse=True))

        
    def _update_candidates(self, n, random_sampling=True):
        # remove candidates that should not be considered any more
        _candidate_dict = defaultdict() 
        for candidate in self._candidate_dict.keys():
            if candidate in self._tomos_done:
                continue
            _candidate_dict[candidate] = self._candidate_dict[candidate]
        self._candidate_dict = _candidate_dict
        
        # add candidates that have been picked once
        if len(self._candidate_dict) < n:
            for i in self._tomos_one_pick:
                self._candidate_dict[i] = 1
                if len(self._candidate_dict) == n:
                    break

        # add candidates that have not been picked yet 
        if len(self._candidate_dict) < n:
            residuals = self._all - self._tomos_done - self._tomos_one_pick
            residuals = deque(residuals)     
            while residuals and len(self._candidate_dict) < n:
                if random_sampling:
                    new_id = random.randint(0, len(residuals) - 1)
                    self._candidate_dict[residuals[new_id]] = 0
                    del residuals[new_id]       
                else:
                    new_candidate = residuals.popleft()
                    self._candidate_dict[new_candidate] = 0
        

    def candidates(self, n: int, random_sampling=True) -> dict:
        self._candidate_dict = {k: 0 for k in range(n)} if not random_sampling else {k: 0 for k in random.sample(range(len(self.root.runs)), n)}
        self._update_candidates(n, random_sampling) 
        return {k: v for k, v in sorted(self._candidate_dict.items(), key=lambda x: x[1], reverse=True)}
    
    
    def fig_data(self):
        image_dataset = copy.deepcopy(self._im_dataset)
        proteins = copy.deepcopy(self.proteins)
        for name in image_dataset['name']:
            image_dataset['count'].append(proteins[name])
                         
        image_dataset['colors'] = {k: 'rgba' + str(tuple(v)) for k, v in image_dataset['colors'].items()}
        return image_dataset


local_dataset = None

def get_local_dataset():
    global local_dataset
    if local_dataset is None:
        local_dataset = LocalDataset()
    return local_dataset
