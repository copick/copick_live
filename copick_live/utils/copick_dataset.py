import os
from copick.impl.filesystem import CopickRootFSSpec
from collections import defaultdict
import pandas as pd
import zarr
import threading
from copick_live.config import get_config

class CopickDataset:
    def __init__(self):
        config = get_config()
        self.root = CopickRootFSSpec.from_file(config.copick_config_path)
        self.tomogram = None
        self.run_name = None
        self.current_point = None  # current point index
        self.current_point_obj = None  # current point copick object
        self.dt = defaultdict(list)

        # variables for storing points in the current run
        self.all_points = []  # [point_obj,...] unique pick objs from all pickers
        self._point_types = []  # ['ribosome',...]
        self.points_per_obj = defaultdict(
            list
        )  # {'ribosome': [(0,0.12),(2,0.33),(3,0.27...],...} (index, score)
        self.all_points_locations = (
            set()
        )  # {(x,y,z),...} a mask to check if a point is duplicated
        # variables for storing picked points in the current run
        self.picked_points_mask = (
            []
        )  # [1, 0, 2, 3, ...] # 1: accept, 2: reject, 0: unassigned, 3: assigned new class
        self._picked_id_per_obj = defaultdict(list)  # {'ribosome': [0,3...],...}
        self._picked_points_per_obj = defaultdict(
            list
        )  # {'ribosome': [point_obj...],...}

        self._logs = defaultdict(
            list
        )  # {'user_id':[], 'x': [], 'y':[], 'z':[], 'operation':['reject', 'accept', 'reassign'], 'start_class':[], 'end_class'[]}
        self.tomogram_lock = threading.Lock()
        self.tomogram_loaded = threading.Event()        

    def _reset_states(self):
        self.points_per_obj = defaultdict(list)
        self._point_types = []
        self.all_points = []
        self.picked_points_mask = []
        self._picked_id_per_obj = defaultdict(list)
        self._picked_points_per_obj = defaultdict(list)
        self.all_points_locations = set()
        self._logs = defaultdict(list)
        self.dt = defaultdict(list)

    def load_curr_run(self, run_name=None, sort_by_score=False, reverse=False):
        if run_name is not None:
            self._reset_states()
            self.run_name = run_name
            self.run = self.root.get_run(self.run_name)
            
            # Start loading tomogram in a separate thread
            threading.Thread(target=self._load_tomogram, args=(run_name,)).start()

            # Load other data
            self._load_points()
            
            if sort_by_score:
                self._sort_points(reverse)


    def _load_tomogram(self, run_name):
        with self.tomogram_lock:
            _run = self.tomo_root.get_run(run_name) if self.tomo_root is not None else self.run
            tomogram = _run.get_voxel_spacing(10).get_tomogram("denoised")
            group = zarr.open(tomogram.zarr())
            _, array = list(group.arrays())[0]
            self.tomogram = array[:]
        self.tomogram_loaded.set()                

    def _store_points(self, obj_name=None, session_id="18"):
        if obj_name is not None:
            _picks = self.run.get_picks(
                object_name=obj_name, user_id=self.root.user_id, session_id=session_id
            )
            if not _picks:
                _picks = self.run.new_picks(
                    object_name=obj_name,
                    user_id=self.root.user_id,
                    session_id=session_id,
                )
                _picks = self.run.get_picks(
                    object_name=obj_name,
                    user_id=self.root.user_id,
                    session_id=session_id,
                )
            _pick_set = _picks[0]
            _pick_set.points = self._picked_points_per_obj[obj_name]
            _pick_set.store()

    def new_user_id(self, user_id=None):
        if user_id is not None:
            config = get_config()
            config.config["user_id"] = user_id

    def load_curr_point(self, point_id=None, obj_name=None):
        if point_id is not None and obj_name is not None:
            self.pickable_obj_name = obj_name
            print("Creating current pick point")
            if len(self.points_per_obj[obj_name]):
                self.current_point = self.points_per_obj[obj_name][point_id][
                    0
                ]  # current point index
                self.current_point_obj = self.all_points[self.current_point]
            else:
                self.current_point = None
                self.current_point_obj = None

    def change_obj_name(self, obj_name=None, enable_log=True):
        if enable_log:
            self.log_operation(
                operation="reasign",
                old_obj_name=self._point_types[self.current_point],
                new_obj_name=obj_name,
            )

        if obj_name is not None and self.current_point is not None:
            self._point_types[self.current_point] = obj_name

    def _update_logs(
        self, operation="placeholder", old_obj_name="NC", new_obj_name="NC"
    ):
        self._logs["run_name"].append(self.run_name)
        self._logs["user_id"].append(self.root.config.user_id)
        self._logs["x"].append(self.current_point_obj.location.x)
        self._logs["y"].append(self.current_point_obj.location.y)
        self._logs["z"].append(self.current_point_obj.location.z)
        self._logs["operation"].append(operation)
        self._logs["start_class"].append(old_obj_name)
        self._logs["end_class"].append(new_obj_name)

    def log_operation(self, operation=None, old_obj_name=None, new_obj_name=None):
        self._logs = defaultdict(list)
        if os.path.exists("logs.csv") == False:
            self._update_logs()
            pd.DataFrame(self._logs).to_csv("logs.csv", sep="\t", index=False)

        df = pd.read_csv("logs.csv", sep="\t")
        self._logs = df.to_dict("list") if len(df) else defaultdict(list)

        if (
            operation is not None
            and old_obj_name is not None
            and new_obj_name is not None
        ):
            self._update_logs(operation, old_obj_name, new_obj_name)
            df = pd.DataFrame.from_dict(self._logs)
            df.to_csv("logs.csv", sep="\t", index=False)

    def handle_accept(self):
        if self.current_point is not None:
            self.picked_points_mask[self.current_point] = 1
            obj_name = self._point_types[self.current_point]
            print(
                f"Accept, Object Type: {obj_name}, Run Name: {self.run_name}, Location: {self.current_point_obj.location}"
            )
            self._point_types[self.current_point] = obj_name
            if self.current_point not in self._picked_id_per_obj[obj_name]:
                self._picked_id_per_obj[obj_name].append(self.current_point)
                self._picked_points_per_obj[obj_name].append(self.current_point_obj)
            self._store_points(obj_name)

    def handle_reject(self, enable_log=True):
        if enable_log:
            self.log_operation(operation="reject", old_obj_name="NC", new_obj_name="NC")

        if self.current_point is not None:
            self.picked_points_mask[self.current_point] = 2
            try:
                obj_name = self._point_types[self.current_point]
                index = self._picked_id_per_obj[obj_name].index(self.current_point)
                print(
                    f"reject point index {self.current_point}, index in the list {index}"
                )
                self._picked_id_per_obj[obj_name].pop(index)
                self._picked_points_per_obj[obj_name].pop(index)
                self._store_points(obj_name)
            except:
                pass

    def handle_assign(self, new_bj_name=None):
        self.handle_reject(enable_log=False)
        self.change_obj_name(new_bj_name)
        self.handle_accept()
        # self.picked_points_mask[self.current_point] = 3

        # EXPERIMENT, dangeraous, may incurr index errors!
        # Only re-assignment changes the original states (initialized when load run)
        new_list = []
        target = tuple()
        old_obj_name = self.pickable_obj_name
        print(old_obj_name, self.points_per_obj[old_obj_name])
        for item in self.points_per_obj[old_obj_name]:
            if item[0] != self.current_point:
                new_list.append(item)
            else:
                target = item

        self.points_per_obj[old_obj_name] = new_list
        # add the new assigned point to the front
        self.points_per_obj[new_bj_name].insert(0, target)

    def handle_accept_batch(self, point_ids=None, obj_name=None):
        if point_ids is not None:
            for point_id in point_ids:
                self.load_curr_point(point_id=point_id, obj_name=obj_name)
                self.handle_accept()

    def handle_reject_batch(self, point_ids=None, obj_name=None):
        if point_ids is not None:
            for point_id in point_ids:
                self.load_curr_point(point_id=point_id, obj_name=obj_name)
                self.handle_reject()

    def handle_assign_batch(self, point_ids=None, obj_name=None, new_bj_name=None):
        if point_ids is not None and obj_name is not None and new_bj_name is not None:
            for point_id in point_ids:
                self.load_curr_point(point_id=point_id, obj_name=obj_name)
                self.handle_assign(new_bj_name)

copick_dataset = None

def get_copick_dataset():
    global copick_dataset
    if copick_dataset is None:
        copick_dataset = CopickDataset()
    return copick_dataset
