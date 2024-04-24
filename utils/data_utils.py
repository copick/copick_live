import random, json, copy, configparser, os
from collections import defaultdict
from copick.impl.filesystem import CopickRootFSSpec


config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"))
COPICK_CONFIG_PATH = './%s' % config['copick']['COPICK_CONFIG_PATH']

class Dataset:
    def __init__(self, config_path: str=None):
        self.config_path = config_path
        self.root = CopickRootFSSpec.from_file(self.config_path) if self.config_path else None
        self.tomos_picked = defaultdict(int)   #{'Test_001': 2, ...}
        self.tomos_per_person = defaultdict(list) #{'Tom': ['Test_001', 'Test_002'], ..}
        self.num_per_person_ordered = dict() # {'Tom':5, 'Julie':3, ...}
        self.proteins = defaultdict(int) # {'ribosome': 38, ...}
        
        self.all = set([i for i in range(1000)])
        self.tomos_one_pick = set() # {0, 1, 2, ...}
        self.candidate_dict = dict() # {1:1, 2:0, ...}
    
        with open(self.config_path) as f:
            config = json.load(f)

        xdata = []
        colors = []
        labels = dict()
        for po in config["pickable_objects"]:
            if po["name"] == "background":
                continue
            xdata.append(po["name"])
            colors.append(po["color"])
            labels[po["name"]] = po["label"]

        self.im_dataset = {'name': xdata, 
                           'count': [0]*len(xdata), 
                           'labels': labels, 
                           'colors': colors
                          }
        
    
    def refresh(self):
        self.root.refresh()
        self._update_tomo_sts()

    
    def _update_tomo_sts(self):
        tomos_per_person = defaultdict(list) 
        num_per_person = dict() 
        proteins = defaultdict(int) 
        tomos_one_pick = set() 
        
        for run in self.root.runs:  # TS_001_1 -> 2 spacings -> processings
            self.tomos_picked[run.name] = len(run.picks)
            if len(run.picks) == 1: # seems always have .name in the pick?
                tomos_one_pick.add(int(run.name))
            
            for pick in run.picks:
                try:
                    file = pick.load()
                except:
                    continue
                proteins[file.pickable_object_name] += 1
                tomos_per_person[file.user_id].append(file.run_name)
        
        self.proteins = proteins
        self.tomos_per_person = tomos_per_person
        self.tomos_one_pick = tomos_one_pick
        
        for p,l in self.tomos_per_person.items():
            num_per_person[p] = len(l)
        self.num_per_person_ordered = dict(sorted(num_per_person.items(), key=lambda item: item[1]))


    def _update_candidates(self, n):
        for candidate in self.candidate_dict.keys():
            candidate_key = 'Test_{:03d}'.format(candidate)
            if candidate_key in self.tomos_picked and self.tomos_picked[candidate_key] >= 2:
                del self.candidate_dict[candidate]
        
        if len(self.candidate_dict) < n:
            for i in self.tomos_one_pick:
                self.candidate_dict[i] = 1
                if len(self.candidate_dict) == n:
                    break
                
        if len(self.candidate_dict) < n:
            k = n - len(self.candidate_dict) 
            residuals = self.all - set([int(i.split('_')[1]) for i in self.tomos_picked.keys()])
            for j in random.choices(list(residuals), k=k):
                self.candidate_dict[j] = 0


    def candidates(self, n: int) -> dict:
        self._update_candidates(n)
        return self.candidate_dict
    
    
    def fig_data(self):
        image_dataset = copy.deepcopy(self.im_dataset)
        for name,count in self.proteins.items():
            if image_dataset['labels'].get(name):
                idx = image_dataset['labels'][name] - 2
                image_dataset['count'][idx] = count
                
        image_dataset['colors'] = ['rgb'+str(tuple(i)) for i in image_dataset['colors']]
        return image_dataset


dataset = Dataset(COPICK_CONFIG_PATH)