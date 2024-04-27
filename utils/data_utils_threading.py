import os, pathlib, time
import threading 
import json

import random, json, copy, configparser, os
from collections import defaultdict
import json


config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"))
COPICK_CONFIG_PATH = '%s' % config['copick']['COPICK_CONFIG_PATH']
COUNTER_FILE_PATH = '%s' % config['counter']['COUNTER_FILE_PATH'] 
LOCAL_FILE_PATH = '%s' % config['local']['LOCAL_FILE_PATH'] + '/ExperimentRuns' 

dirs = ['TS_'+str(i)+'_'+str(j) for i in range(1, 122) for j in range(1,10)]
dir2id = {j:i for i,j in enumerate(dirs)}

with open(COPICK_CONFIG_PATH) as f:
    copick_config_file = json.load(f)


# define a wrapper function
def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def fig_data(config):
        xdata = []
        colors = []
        labels = dict()
        for po in config["pickable_objects"]:
            if po["name"] == "background":
                continue
            xdata.append(po["name"])
            colors.append(po["color"])
            labels[po["name"]] = po["label"]

        im_dataset = {'name': xdata, 
                      'count': [0]*len(xdata), 
                      'labels': labels, 
                      'colors': colors
                    }
        return im_dataset


class Dataset:
    def __init__(self, local_file_path: str=None, config_path: str=None):
        self.root = local_file_path
        with open(config_path) as f:
            self.config_file = json.load(f)
        
        self.proteins = defaultdict(int) # {'ribosome': 38, ...}
        self.tomograms = defaultdict(set)  #{'TS_1_1':{'ribosome', ...}, ...}
        self.tomos_per_person = defaultdict(set) #{'john.doe':{'TS_1_1',...},...} 
        self.tomos_pickers = defaultdict(set)   #{'Test_001': {john.doe,...}, ...}

        # output
        self.tomos_picked = defaultdict(int)   #{'Test_001': 2, ...}
        self.num_per_person_ordered = dict() # {'Tom':5, 'Julie':3, ...}
        
        # hidden variables
        self.all = set([i for i in range(1000)])
        self.tomos_one_pick = set() # {0, 1, 2, ...}
        self.candidate_dict = defaultdict() # {1:1, 2:0, ...}
        self.candidate_dict_new = defaultdict() #{1:1, 2:0, ...}
        self.prepicks = set(['slab-picking', 'pytom-template-match', 'relion-refinement', 'prepick', 'ArtiaX', 'default']) 

        xdata = []
        colors = []
        labels = dict()
        for po in self.config_file["pickable_objects"]:
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

    def _reset(self):
        self.proteins = defaultdict(int) 
        self.tomograms = defaultdict(set) 
        self.tomos_per_person = defaultdict(set) 
        self.tomos_pickers = defaultdict(set)
        self.tomos_picked = defaultdict(int)   
        self.num_per_person_ordered = dict()
        self.candidate_dict = defaultdict() 
        self.candidate_dict_new = defaultdict() 

        xdata = []
        colors = []
        labels = dict()
        for po in self.config_file["pickable_objects"]:
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
        self._reset()
        self._update_tomo_sts()

    @threaded
    def _walk_dir(self, args):
        r, s, e = args
        for dir in dirs[s:e]:
            dir_path = r + '/' + dir +'/Picks'
            if os.path.exists(dir_path):
                for json_file in pathlib.Path(dir_path).glob('*.json'):
                    contents = json.load(open(json_file))
                    if contents['user_id'] not in self.prepicks:
                        self.tomos_per_person[contents['user_id']].add(contents['run_name'])
                        self.tomograms[contents['run_name']].add(contents['pickable_object_name']) 
                        self.tomos_pickers[contents['run_name']].add(contents['user_id'])
                        self.proteins[contents['pickable_object_name']] += len(contents['points'])
                        

    def _update_tomo_sts(self):
        start = time.time() 
        seg = round(len(dirs)/6)
        args1 = (self.root, 0, seg)
        args2 = (self.root, seg, seg*2)
        args3 = (self.root, seg*2, seg*3)
        args4 = (self.root, seg*3, seg*4)
        args5 = (self.root, seg*4, seg*5)
        args6 = (self.root, seg*5, len(dirs))

        t1 = self._walk_dir(args1)
        t2 = self._walk_dir(args2)
        t3 = self._walk_dir(args3)
        t4 = self._walk_dir(args4)
        t5 = self._walk_dir(args5)
        t6 = self._walk_dir(args6)

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
        print(f'{time.time()-start} s to check all files')
        
        
        for tomo, pickers in self.tomograms.items():
            if len(pickers) == 1:
                self.tomos_one_pick.add(dir2id[tomo])

        self.tomos_picked = {i:len(k) for i,k in self.tomograms.items()}
        self.num_per_person_ordered = dict(sorted(self.tomos_per_person.items(), key=lambda item: len(item[1]), reverse=True))



    def _update_candidates(self, n, random_sampling=True):
        for candidate in self.candidate_dict.keys():
            candidate_key = dirs[candidate]
            if candidate_key in self.tomos_picked and self.tomos_picked[candidate_key] < 2:
                self.candidate_dict_new[candidate] = self.tomos_picked[candidate_key]
        
        self.candidate_dict = self.candidate_dict_new
        
        if len(self.candidate_dict) < n:
            for i in self.tomos_one_pick:
                self.candidate_dict[i] = 1
                if len(self.candidate_dict) == n:
                    break
                
        if len(self.candidate_dict) < n:
            k = n - len(self.candidate_dict) 
            residuals = self.all - set([int(i.split('_')[1]) for i in self.tomos_picked.keys()])
            if random_sampling:
                for j in random.choices(list(residuals), k=k):
                    self.candidate_dict[j] = 0
            else:
                for j in list(residuals)[:k]:
                    self.candidate_dict[j] = 0


    def candidates(self, n: int, random_sampling=True) -> dict:
        self._update_candidates(n, random_sampling)
        return self.candidate_dict
    
    
    def fig_data(self):
        image_dataset = copy.deepcopy(self.im_dataset)
        for name,count in self.proteins.items():
            if image_dataset['labels'].get(name):
                idx = image_dataset['labels'][name] - 2
                image_dataset['count'][idx] = count
                
        image_dataset['colors'] = ['rgb'+str(tuple(i)) for i in image_dataset['colors']]
        return image_dataset


dataset = Dataset(LOCAL_FILE_PATH, COPICK_CONFIG_PATH)