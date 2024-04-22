from copick.impl.filesystem import CopickRootFSSpec
# import zarr
from collections import defaultdict
import random


class Dataset:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.root = CopickRootFSSpec.from_file(self.file_path)
        self.tomos_picked = defaultdict(int)   #{'Test_001': 2, ...}
        self.tomos_per_person = defaultdict(list) #{'Tom': ['Test_001', 'Test_002'], ..}
        self.num_per_person_ordered = dict() # {'Tom':5, 'Julie':3, ...}
        self.proteins = defaultdict(int) # {'ribosome': 38, ...}
        
        self.all = set([i for i in range(1000)])
        self.tomos_one_pick = set() # (0, 1, 2, ...)
    
    def refresh(self):
        self.root = CopickRootFSSpec.from_file(self.file_path)
        self._update_tomo_sts()

    def _update_tomo_sts(self):
        tomos_per_person = defaultdict(list) #{'Tom': ['Test_001', 'Test_002'], ..}
        num_per_person = dict() # {'Tom':5, 'Julie':3, ...}
        proteins = defaultdict(int) # {'ribosome': 38, ...}
        tomos_one_pick = set() 
        for run in self.root.runs:  # TS_001
            self.tomos_picked[run.name] = len(run.picks)
            if len(run.picks) == 1:
                tomos_one_pick.add(int(run.name))
            
            for pick in run.picks:
                file = pick.load()
                proteins[file['pickable_object_name']] += 1
                tomos_per_person[file['user_id']].append(file['run_name'])
        
        self.proteins = proteins
        self.tomos_per_person = tomos_per_person
        self.tomos_one_pick = tomos_one_pick
        
        for p,l in self.tomos_per_person:
            num_per_person[p] = len(l)
        self.num_per_person_ordered = dict(sorted(num_per_person.items(), key=lambda item: item[1]))

    def candidates(self, n: int) -> list:
        res = list(self.tomos_one_pick)
        if n <= len(self.tomos_one_pick):
            res = res[:n]
        else:
            k = n - len(self.tomos_one_pick)
            residuals = self.all - set([int(i.split('_')[1]) for i in self.tomo_picked.keys()])
            res.extend(random.choices(list(residuals), k=k)) 
        return res


            