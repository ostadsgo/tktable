import os
import glob
import numpy as np
import copy


class Track_Event:
    def __init__(self):
        self.outer_ccw = [
            "EAST-STRAIGHT",
            "NORTH-STRAIGHT",
            "CORNER-BUMPS",
            "WEST-STRAIGHT",
        ]
        self.corrugation = ["CORRUGATIONS"]
        self.Inner_loop = [
            "BELGIAN-BLOCK",
            "NORTH-TURN",
            "BROKEN-CONCRETE",
            "CROSS-DITCHES",
            "POTHOLES",
        ]
        self.outer_cw = [
            "WEST-STRAIGHT",
            "CORNER-BUMPS",
            "NORTH-STRAIGHT",
            "EAST-STRAIGHT",
        ]
        self.other_events = [
            "S-TURN",
            "EIGHTS",
            "OL-HS-CW-TEST",
            "OL-HS-CCW-TEST",
            "TWISTER-BLOCKS",
            "ROLLING-STONES-2",
            "I40-RIDE",
            "OL-CCW-TEST",
            "BRIDGE-CONNECTION",
            "ROLLING-STONES-3",
            "CORNER-BUMPS-CCW",
            "CHASSIS-TWISTER",
            "CROSS-ART-RAMP-OPC3",
            "CROSS-ART-RAMP-OPC2",
            "IL-TEST",
            "INNER-LOOP",
            "CONST-HUMPS",
            "RUT-ROAD",
            "GROUND-TWIST",
            "GROUND-TWIST-CW",
            "CORRUGATIONS-2023",
            "INNER-LOOP-2023",
            "OUTER-LOOP-CC-2023",
            "OUTER-LOOP-CW-2023",
        ]

        self.full_daq = (
            self.outer_ccw + self.corrugation + self.Inner_loop + self.outer_cw
        )
        self.all_events_db = self.all_events_name()

    def all_events_name(self):
        path_ = "/caeapps/vtc/trucklib/cvm2/db/tloads/"

        all_test_events = list()
        for root, dirs, files in os.walk(path_):
            for dir_ in dirs:
                if dir_ not in all_test_events:
                    all_test_events.append(dir_)

        # extra = ['CORRUGATIONS-2023', 'INNER-LOOP-2023', 'OUTER-LOOP-CC-2023', 'OUTER-LOOP-CW-2023']
        for i in self.other_events:
            if i not in all_test_events:
                all_test_events.append(i)
        return all_test_events


class RFile:
    def __init__(self, r_path_folder):
        self.r_path_folder = r_path_folder
        self.node_list = list()
        self.r_folder = str
        self.track = Track_Event()

    def read_file(self, f_n):
        with open(f_n) as f:
            cnt = f.read().split("\n")
        return cnt

    def grab_t_amp(self, f_n):
        cnt = self.read_file(f_n)
        time_arr = list()
        amplitude = list()
        for l in cnt:
            if len(l.strip()) > 1:
                ll = l.split()
                time_arr.append(float(ll[0]))
                amplitude.append(float(ll[-1]))

        time_arr = np.array(time_arr)
        amplitude = np.array(amplitude)
        return time_arr, amplitude

    def check_all_dir(self):
        os.chdir(self.r_path_folder)
        cur_dir = os.getcwd()
        flag = True
        for i in self.track.full_daq:
            sch_path = os.path.join(cur_dir, i)
            if os.path.exists(sch_path):
                flag = True
            else:
                flag = False
                break
        return flag, i

    def find_all_grid(self):
        cur_dir = os.getcwd()
        all_gs = list()
        for test_ev in list(set(self.track.all_events_db)):
            to_check = os.path.join(cur_dir, test_ev)
            if os.path.exists(to_check):
                os.chdir(to_check)
                r_files = glob.glob("*.R")
                for r_f in r_files:
                    if r_f.startswith("ACCE"):
                        grid_id = r_f[:-2].split("ACCE")[-1].rsplit("_", 1)[0]
                        if grid_id not in all_gs:
                            all_gs.append(grid_id)

        os.chdir("../")
        return all_gs

    def grid_track_dict(self, all_gs):
        cur_dir = os.getcwd()
        dirs = ["T1", "T2", "T3"]
        all_events = self.track.all_events_db

        g_dict = {}

        for g_num in all_gs:
            g_dict[g_num] = {}
            for d in dirs:
                g_dict[g_num][d] = {}
                for folder in all_events:
                    path = os.path.join(cur_dir, folder)
                    if os.path.exists(path):
                        g_dict[g_num][d][folder] = {"time": [], "amp": []}
                        os.chdir(path)
                        g_path = f"ACCE{g_num}_{d}.R"
                        if os.path.exists(g_path):
                            t, amp = self.grab_t_amp(g_path)
                            a_list = [t, amp]
                            g_dict[g_num][d][folder]["time"] = a_list[0]
                            g_dict[g_num][d][folder]["amp"] = a_list[1]
                            os.chdir("../")

        return g_dict

    def clean_empty(self, a_dict):
        b_dict = {}

        for grid_id, grid_data in a_dict.items():
            b_dict[grid_id] = {}
            for direction, events in grid_data.items():
                for event, values in events.items():
                    time_data = values.get("time")
                    if len(time_data) != 0:
                        # Initialize the direction if it doesn't exist
                        if direction not in b_dict[grid_id]:
                            b_dict[grid_id][direction] = {}
                        # Add the event with its 'time' and 'amp' values
                        b_dict[grid_id][direction][event] = {
                            "time": np.array(time_data, dtype=np.float64),
                            "amp": np.array(values.get("amp"), dtype=np.float64),
                        }

                        if time_data[0] != 0:
                            new_time = self.reset_time(time_data)
                            b_dict[grid_id][direction][event]["time"] = new_time

        return b_dict

    def reset_time(self, time_list):
        t2 = str(time_list[1])
        t1 = str(time_list[0])

        t_delta = Decimal(t2) - Decimal(t1)
        t_0 = Decimal(t2) - Decimal(t2)
        t_0 = str(t_0)
        t_0 = float(t_0)
        t_delta = str(t_delta)
        t_delta = float(t_delta)

        new_time = list()
        start_t = t_0
        for i in time_list:
            new_time.append(start_t)
            start_t += t_delta

        new_time = np.array(new_time, np.float64)

        return new_time

    def reorder_time(self, time_list, start_t):
        t2 = str(time_list[1])
        t1 = str(time_list[0])

        t_delta = Decimal(t2) - Decimal(t1)

        new_time = list()
        start_t = start_t + t_delta
        for i in time_list:
            new_time.append(start_t)
            start_t += t_delta

        return new_time

    def time_gap(self, time_in_sec, start_t, time_delta):
        number_of_step = int(time_in_sec / time_delta)

        new_time = list()
        start_t = start_t + time_delta
        for i in range(number_of_step):
            new_time.append(start_t)
            start_t += time_delta

        return new_time

    def event_name_func(self, event_name):
        event_list = None
        if event_name == "outer_ccw":
            event_list = [
                "EAST-STRAIGHT",
                "NORTH-STRAIGHT",
                "CORNER-BUMPS",
                "WEST-STRAIGHT",
            ]
        elif event_name == "Corrugation":
            event_list = ["CORRUGATIONS"]
        elif event_name == "inner_loop":
            event_list = [
                "BELGIAN-BLOCK",
                "NORTH-TURN",
                "BROKEN-CONCRETE",
                "CROSS-DITCHES",
                "POTHOLES",
            ]
        elif event_name == "outer_cw":
            event_list = [
                "WEST-STRAIGHT",
                "CORNER-BUMPS",
                "NORTH-STRAIGHT",
                "EAST-STRAIGHT",
            ]

        return event_list

    def event_sorter(self, dict_data, event_list):
        for g in dict_data:
            for dirs in dict_data.get(g):
                a_dict = dict_data[g][dirs]
                sorted_keys = sorted(
                    a_dict.keys(),
                    key=lambda x: event_list.index(x)
                    if x in event_list
                    else float("inf"),
                )
                sorted_dict = {key: a_dict[key] for key in sorted_keys}
                dict_data[g][dirs] = sorted_dict
        return dict_data

    def convert_to_g(self, data_dict):
        data_dict2 = self.clean_empty(data_dict)
        new_dict = copy.deepcopy(data_dict2)

        for g in data_dict2:
            for dirs in data_dict2[g]:
                for ev in data_dict2[g][dirs]:
                    amp = data_dict2[g][dirs][ev].get("amp")
                    amp_max = max(amp)
                    if amp_max > 100:
                        new_amp = amp / 9810
                        new_dict[g][dirs][ev]["amp"] = new_amp

        return new_dict

    def shorten_evnt(self, ev, t, amp):
        shorten_dict = {
            "EAST-STRAIGHT": [0, 17],
            "NORTH-STRAIGHT": [0, 12],
            "CORNER-BUMPS": [0.1, 6],
            "WEST-STRAIGHT": [1, 22],
            "CORRUGATIONS": [0.5, 14.0],
            "BELGIAN-BLOCK": [1.2, 8],
            "NORTH-TURN": [2, 10.2],
            "BROKEN-CONCRETE": [0.1, 6.0],
            "CROSS-DITCHES": [0.5, 4.8],
            "POTHOLES": [0.75, 3.2],
        }

        upper_limit = shorten_dict.get(ev)[1]
        lower_limit = shorten_dict.get(ev)[0]
        new_t = list()
        new_amp = list()

        for value, amp_val in zip(t, amp):
            if value < lower_limit:
                continue
            if value > upper_limit:
                break
            new_t.append(value)
            new_amp.append(amp_val)

        new_t2 = self.reorder_time(new_t, 0)

        return new_t2, new_amp

    def event_seq_creator(self, dict_data, event_list):
        a_name = "outer_ccw"
        new_data = {k: {"T1": {}, "T2": {}, "T3": {}} for k in dict_data}
        for g in dict_data:
            for dirs in dict_data[g]:
                new_data[g][dirs] = {a_name: {"time": [], "amp": []}}
                t_list = list()
                amp_list = list()

                for ev_count, ev in enumerate(event_list):
                    t_ = dict_data[g][dirs][ev].get("time")
                    amp_ = dict_data[g][dirs][ev].get("amp")
                    t, amp = self.shorten_evnt(ev, t_, amp_)

                    if ev_count == 0:
                        t_list.extend(t)
                        amp_list.extend(amp)
                    if ev_count > 0:
                        t = self.reorder_time(t, t_list[-1])
                        t_list.extend(t)
                        amp_list.extend(amp)

                new_data[g][dirs][a_name].get("time").extend(t_list)
                new_data[g][dirs][a_name].get("amp").extend(amp_list)
        return new_data

    def create_s3t_fron_r(self):
        temp_t = "cmulti *20720001*_T* *20720003*_T* *20720004*_T* *20720005*_T* *20720006*_T* *20720002*_T* "
        all_folder_name = [name for name in os.listdir(".") if os.path.isdir(name)]
        for name in all_folder_name:
            path = f"./{name}"
            if os.path.exists(path):
                os.chdir(path)
                r_files = glob.glob("*.R")
                if len(r_files) == 0:
                    os.chdir("../")
                    continue
                else:
                    if len(r_files) > 0:
                        os.system(temp_t)
                        os.chdir("../")
        return 0
