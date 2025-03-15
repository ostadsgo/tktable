import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, Menu
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import SpanSelector

# import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, argrelextrema
from scipy import stats
import matplotlib.pyplot as plt

# import read_signal_csv  # Assuming this is the class where you handle the CSV logic
from decimal import Decimal
import glob
import shutil
import threading
import matplotlib.gridspec as gridspec
from scipy.signal import welch
from scipy.signal import find_peaks
from scipy.fft import fft
import copy
import csv
from scipy.interpolate import interp1d
from scipy.signal import decimate
from matplotlib.ticker import MaxNLocator
import pandas as pd
import pyarrow.csv as pv

import tempfile


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


class R_file:
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


class CSVSignal:
    """Handles operations related to CSV signals."""

    def __init__(self, csv_loc, csv_dict, f_name):
        self.csv_loc = csv_loc
        self.csv_dict = csv_dict
        self.f_name = f_name

    def extract_val(self):
        """Extract time and amplitude values from the CSV."""
        t = self.csv_dict[self.f_name][self.csv_loc].get("time")
        amp = self.csv_dict[self.f_name][self.csv_loc].get("amp")
        amp = np.array(amp, dtype=np.float64)
        return t, amp

    def reorder_time(self, time_array, start_t):
        """Reorder time values starting from a given time."""
        # Calculate the time delta
        t_delta = time_array[1] - time_array[0]
        # Generate the new time values
        new_time = start_t + np.arange(len(time_array)) * t_delta
        return new_time


class Grid:
    """Handles operations related to grids in the data."""

    def __init__(self, grid_id, grid_dict):
        self.grid_id = grid_id
        self.grid_dict = grid_dict

    def get_grid_dir(self):
        """Get all directories related to the grid."""
        return list(self.grid_dict.get(self.grid_id).keys())

    def get_grid_event(self, dirs):
        """Get all events in a directory."""
        return list(self.grid_dict[self.grid_id][dirs].keys())

    def extract_val(self, dirs, ev):
        """Extract time and amplitude values for a specific event."""
        t = self.grid_dict[self.grid_id][dirs][ev].get("time")

        amp = self.grid_dict[self.grid_id][dirs][ev].get("amp")

        return t, amp


class Utils:
    """Utility functions for handling file operations."""

    def __init__(self):
        self.complete = 0

    @staticmethod
    def check_file_creation(f_name):
        """Check file creation time."""
        return os.path.getctime(f_name)

    @staticmethod
    def compare_file_current_time(file_create_time, current_time):
        """Compare file creation time with the current time."""
        return file_create_time > current_time

    def create_csv_from_s3t_rsp(self, folder_name, file_type):
        """Convert RSP/S3T files to CSV format."""
        rsp_list = self.find_all_rsps(folder_name, file_type)
        return rsp_list

    @staticmethod
    def find_all_rsps(dirname, file_type):
        """Find all RSP/S3T files in a directory."""
        os.chdir(dirname)
        return glob.glob(file_type)

    @staticmethod
    def process_rsp_file(rsp, flo_path):
        """Process an individual RSP file for conversion."""
        extra_files = []
        rsp_base = os.path.basename(rsp)[:-4]
        sh_rsp, script_rsp, log_rsp = (
            f"{rsp_base}_{suffix}"
            for suffix in ["sh_file.sh", "script_file.script", "log_file.log"]
        )
        rsp_full_path = os.path.abspath(rsp)
        extra_files.extend([sh_rsp, script_rsp, log_rsp])

        for f in extra_files:
            os.system(f"touch {f}")

        shutil.copy("/nobackup/vol01/a504696/rsp_to_csv/rsp_2_csv.sh", sh_rsp)
        shutil.copy("/nobackup/vol01/a504696/rsp_to_csv/rsp_2_csv.script", script_rsp)

        # Update and execute shell and script files
        Utils.update_file(
            sh_rsp,
            {
                "script_name": os.path.abspath(script_rsp),
                "log_file": os.path.abspath(log_rsp),
                "flo_file": flo_path,
            },
        )
        Utils.update_file(script_rsp, {"rsp_file": rsp_full_path})

        os.system(f"./{sh_rsp}")

        # Clean up extra files
        for file in extra_files:
            os.remove(file)

    @staticmethod
    def update_file(file_path, replacements):
        """Update content in a file based on given replacements."""
        with open(file_path) as f:
            content = f.read()
        for key, value in replacements.items():
            content = content.replace(key, value)
        with open(file_path, "w") as f:
            f.write(content)


class DataSingelton:
    _instance = None
    cvm_data = {}
    cvm_data_copy = {}
    test_data = {}
    sim_combine = {}
    sim_combin_string = ""
    original_g_dict = {}
    original_test_dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataSingelton, cls).__new__(cls)
        return cls._instance


class ReadSignalFrame(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.notebook = notebook
        self.flag_daq = None
        self.ev_not_exist = None
        self.flag_csv_file = dict()
        self.csv_dict = dict()
        self.csv_old_time = dict()
        self.csv_file = list()
        self.utils = Utils()
        self.file_type = None
        self.grid_data = []
        self.csv_point = []
        # self.color_dict = {i: plt.get_cmap('tab20')(i / 15) for i in range(15)}
        self.color_dict = {
            i: (
                plt.get_cmap("tab20")(i / 20)
                if i < 20
                else plt.get_cmap("tab20b")((i - 20) / 10)
            )
            for i in range(30)
        }
        initial_path = os.path.dirname(os.path.abspath(__file__))
        self.r_f = R_file(initial_path)
        self.shared_data = DataSingelton()
        self.help_func = Help_utils()

        self.ui()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.start_time = time.time()

    def ui(self):
        # Main content frame (middle frame setup)
        self.middle_frame = tk.Frame(self)
        self.middle_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.setup_middle_frame(self.middle_frame)

    def setup_middle_frame(self, frame):
        self.left_frame = tk.Frame(frame)
        self.plot_frame = tk.Frame(frame)
        self.right_frame_csv = tk.Frame(frame)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=10)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(0, weight=10)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame_csv.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.setup_left_frame(self.left_frame)
        self.setup_plot_frame(self.plot_frame)
        self.setup_right_frame_csv(self.right_frame_csv)

    def setup_left_frame(self, frame):
        label_title_r = tk.Label(
            frame, text="CVM/Simulation DATA", font=("Arial", 14, "bold")
        )
        self.label_daq = tk.Label(frame, text="DAQ complete : None")
        self.listbox_grid = tk.Listbox(frame, exportselection=False)
        self.listbox_direction = tk.Listbox(frame, exportselection=False)
        self.listbox_event = tk.Listbox(
            frame, exportselection=False, selectmode=tk.MULTIPLE
        )
        self.chck_all_var = tk.BooleanVar()
        self.checkbox_sl_all = tk.Checkbutton(
            frame,
            text="Check All",
            variable=self.chck_all_var,
            command=self.func_check_all_sig,
        )
        label_title_r.pack(side="top", pady=5)
        self.label_daq.pack(pady=5)
        self.listbox_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox_direction.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox_event.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.checkbox_sl_all.pack(side=tk.LEFT, padx=5)
        self.listbox_grid.bind("<<ListboxSelect>>", self.on_listbox_grid_select)
        self.listbox_direction.bind("<<ListboxSelect>>", self.on_listbox_select_dir)
        self.listbox_event.bind("<<ListboxSelect>>", self.on_listbox_event)

    def setup_plot_frame(self, frame):
        self.fig, self.ax = plt.subplots(2, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.ax[0].set_title("CVM Signal", fontdict={"weight": "bold"})
        self.ax[1].set_title("Test Signal", fontdict={"weight": "bold"})
        self.fig.tight_layout()

    def setup_right_frame_csv(self, frame):
        label_title_csv = tk.Label(
            frame, text="CSV/Test DATA", font=("Arial", 14, "bold")
        )
        self.label_csv_ok = tk.Label(frame, text="CSV File : None")
        self.listbox_csv = tk.Listbox(
            frame, exportselection=False, selectmode=tk.MULTIPLE, width=50
        )
        self.listbox_csv_file = tk.Listbox(
            frame, exportselection=False, selectmode=tk.SINGLE, width=50
        )
        self.reorder_var = tk.BooleanVar()
        self.checkbox_reorder = tk.Checkbutton(
            frame,
            text="Reorder Time",
            variable=self.reorder_var,
            command=self.reorder_csv_time,
        )
        label_title_csv.pack(side="top", pady=5)
        self.label_csv_ok.pack(pady=5)
        self.listbox_csv_file.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox_csv.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.checkbox_reorder.pack(side=tk.LEFT, padx=5)
        self.listbox_csv.bind("<<ListboxSelect>>", self.on_listbox_csv_select)
        self.listbox_csv_file.bind("<<ListboxSelect>>", self.on_listbox_csv_file_select)

    def func_check_all_sig(self):
        if self.chck_all_var.get():
            self.listbox_event.select_set(0, tk.END)
            try:
                selected_grid_index = self.listbox_grid.curselection()[0]
                selected_direction_index = self.listbox_direction.curselection()[0]
                selected_event_index = self.listbox_event.curselection()
                selected_grid = self.grid_data[selected_grid_index]
                selected_direction = selected_grid.get_grid_dir()[
                    selected_direction_index
                ]
                selected_events = [
                    selected_grid.get_grid_event(selected_direction)[i]
                    for i in selected_event_index
                ]
                ev_dict = {
                    i: selected_grid.extract_val(selected_direction, i)
                    for i in selected_events
                }

                # cvm_data = {'grid': {selected_grid.grid_id:{selected_direction:ev_dict}}}
                self.shared_data.cvm_data = {
                    "grid": {selected_grid.grid_id: {selected_direction: ev_dict}}
                }
                self.shared_data.cvm_data_copy = copy.deepcopy(
                    self.shared_data.cvm_data
                )
                self.plot_data(ev_dict)
            except IndexError:
                pass
        else:
            self.listbox_event.select_clear(0, tk.END)
            ev_dict = {}
            self.shared_data.cvm_data = {}
            self.shared_data.cvm_data_copy = {}
            self.plot_data(ev_dict)

    def reorder_csv_time(self):
        selected_index = self.listbox_csv_file.curselection()[0]
        selected_csv = self.csv_file[selected_index][
            0
        ]  # self.csv_fie contain (file_name complete, basename file_name)
        if self.reorder_var.get():
            if self.csv_point:
                for i in self.csv_point:
                    t, _ = i.extract_val()
                    t_new = i.reorder_time(t, 0)
                    self.csv_dict[selected_csv][i.csv_loc]["time"] = t_new
                self.listbox_csv.selection_clear(0, tk.END)
                self.listbox_csv.selection_anchor(tk.END)
                self.plot_data_csv({})
        else:
            if len(self.csv_point) > 0 and len(self.csv_old_time) > 0:
                for i in self.csv_point:
                    t, _ = i.extract_val()
                    t_new = i.reorder_time(t, self.csv_old_time[selected_csv][0])
                    self.csv_dict[selected_csv][i.csv_loc]["time"] = t_new
                self.listbox_csv.selection_clear(0, tk.END)
                self.listbox_csv.selection_anchor(tk.END)
                self.plot_data_csv({})

    def get_all_elements(self, listbox):
        # Get all elements in the Listbox
        all_elements = listbox.get(0, tk.END)
        return all_elements

    def on_listbox_csv_file_select(self, event):
        # global test_data
        self.listbox_csv.delete(0, tk.END)
        self.csv_point.clear()
        selected_index = self.listbox_csv_file.curselection()[0]
        selected_csv = self.csv_file[selected_index][
            0
        ]  # self.csv_fie contain (file_name complete, basename file_name)
        text = (
            "CSV File : Ok!" if self.flag_csv_file[selected_csv] else "CSV file wrong!"
        )
        self.change_label_text(self.label_csv_ok, text)
        if self.flag_csv_file[selected_csv]:
            all_gs = list(self.csv_dict[selected_csv].keys())
            for grid_id in all_gs:
                self.csv_point.append(CSVSignal(grid_id, self.csv_dict, selected_csv))
                display_text = f"Signal Loc: {grid_id}"
                self.listbox_csv.insert(tk.END, display_text)

            # test_data = {'csv':{}}
            self.shared_data.test_data = {"csv": {}}

    def change_label_text(self, label, text):
        label.config(text=text)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            # self.line_edit.delete(0, tk.END)
            # self.line_edit.insert(0, folder_path)
            self.r_f = R_file(folder_path)
            self.flag_daq, ev = self.r_f.check_all_dir()
            if self.flag_daq != True:
                self.ev_not_exist = ev
            self.display_data()

    ###################################################################################################################
    # TODO: get_row to get data of a row: get_row(0)
    # get_cell_data: to get data of a cell: get_cell_data(row=0, column=2)
    # add_hi -> add hihglight for a row
    # clear_hi -> clear highlight for a row
    # NOTE: future ntoe

    ###################################################################################################################

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv")],
            multiple=False,
        )
        if file_path:
            # self.line_edit_csv.delete(0, tk.END)
            # self.line_edit_csv.insert(0, file_path)
            flag, text = self.help_func.check_csv_format(file_path)

            self.end_time = time.time()
            elapsed_time = self.end_time - self.start_time
            if file_path not in self.csv_file:
                f_ = os.path.basename(file_path)
                v = file_path, f_
                if v not in self.csv_file:
                    if len(self.csv_file) == 0:
                        self.csv_file.append(v)
                    else:
                        self.csv_file.insert(0, v)

            if flag:
                self.flag_csv_file[file_path] = True
                a_dict = self.help_func.pull_csv_data(file_path)
                self.shared_data.original_test_dict = a_dict
                self.end_time = time.time()
                elapsed_time = self.end_time - self.start_time
                first_item = list(a_dict.keys())[0]
                one_time = a_dict[first_item].get("time")
                if file_path not in self.csv_old_time:
                    self.csv_old_time[file_path] = one_time
                if file_path not in self.csv_dict:
                    self.csv_dict[file_path] = a_dict
                    self.display_data_csv(file_path)
                else:
                    messagebox.showerror("Error", "This CSV  already exists!")
                    return 0

            else:
                self.flag_csv_file[file_path] = False
                messagebox.showerror("Error incompatible CSV", text)
                return 0

    def display_data(self):
        self.listbox_grid.delete(0, tk.END)
        self.listbox_direction.delete(0, tk.END)
        self.listbox_event.delete(0, tk.END)
        self.grid_data.clear()

        text = (
            "DAQ complete : Yes!"
            if self.flag_daq
            else f"DAQ complete : No!\nEvent {self.ev_not_exist} missing!"
        )
        self.change_label_text(self.label_daq, text)

        all_gs = self.r_f.find_all_grid()
        g_dict_ = self.r_f.grid_track_dict(all_gs)
        g_dict = self.r_f.convert_to_g(g_dict_)

        self.shared_data.original_g_dict = g_dict

        for grid_id in all_gs:
            self.grid_data.append(Grid(grid_id, g_dict))
            display_text = f"Grid ID: {grid_id}"
            self.listbox_grid.insert(tk.END, display_text)

    def display_data_csv(self, file_path):
        all_elements = self.get_all_elements(self.listbox_csv_file)
        a_file = os.path.basename(file_path)
        if a_file not in all_elements:
            self.listbox_csv_file.insert(0, a_file)

    def on_listbox_csv_select(self, event):
        # global test_data
        selected_csv_point_index = self.listbox_csv.curselection()
        selected_csv = [self.csv_point[i] for i in selected_csv_point_index]
        csv_sel_dict = {}
        for csv_loc in selected_csv:
            t, amp = csv_loc.extract_val()
            csv_sel_dict[csv_loc.csv_loc] = t, amp

        # test_data = {'csv':csv_sel_dict}
        self.shared_data.test_data = {"csv": csv_sel_dict}

        self.plot_data_csv(csv_sel_dict)

    def display_any_list_box(self, listbox, item_list):
        listbox.delete(0, tk.END)
        for item in item_list:
            listbox.insert(tk.END, item)

    def on_listbox_grid_select(self, event):
        try:
            selected_index = self.listbox_grid.curselection()[0]
            selected_grid = self.grid_data[selected_index]

            dirs = selected_grid.get_grid_dir()
            self.display_any_list_box(self.listbox_direction, dirs)
        except IndexError:
            pass

    def on_listbox_select_dir(self, event):
        try:
            selected_grid_index = self.listbox_grid.curselection()[0]
            selected_direction_index = self.listbox_direction.curselection()[0]
            selected_grid = self.grid_data[selected_grid_index]
            selected_direction = selected_grid.get_grid_dir()[selected_direction_index]

            event_info = selected_grid.get_grid_event(selected_direction)
            self.display_any_list_box(self.listbox_event, event_info)
        except IndexError:
            pass

    def on_listbox_event(self, event):
        # global cvm_data
        try:
            selected_grid_index = self.listbox_grid.curselection()[0]
            selected_direction_index = self.listbox_direction.curselection()[0]
            selected_event_index = self.listbox_event.curselection()
            selected_grid = self.grid_data[selected_grid_index]
            selected_direction = selected_grid.get_grid_dir()[selected_direction_index]
            selected_events = [
                selected_grid.get_grid_event(selected_direction)[i]
                for i in selected_event_index
            ]
            ev_dict = {
                i: selected_grid.extract_val(selected_direction, i)
                for i in selected_events
            }
            # cvm_data = {'grid': {selected_grid.grid_id:{selected_direction:ev_dict}}}
            self.shared_data.cvm_data = {
                "grid": {selected_grid.grid_id: {selected_direction: ev_dict}}
            }
            self.shared_data.cvm_data_copy = copy.deepcopy(self.shared_data.cvm_data)
            self.plot_data(ev_dict)
        except IndexError:
            pass

    def plot_data_csv(self, data_dict):
        self.ax[1].cla()  # Clear previous plot

        self.ax[1].set_title("Test Signal", fontdict={"weight": "bold"})
        if not data_dict:
            self.canvas.draw()
            return 0

        for i, (k, value) in enumerate(data_dict.items()):
            if i >= 30:
                messagebox.showinfo(
                    "Information", "Maximum number of 30 plots reached!"
                )
                break

            t_, amplitude = value
            self.ax[1].plot(t_, amplitude, label=k, color=self.color_dict[i])

        # Set the labels and legends
        self.ax[1].set_xlabel("Time")
        self.ax[1].set_ylabel("Amplitude")
        self.ax[1].legend()

        # Draw the new plot
        self.canvas.draw()

    def plot_data(self, data_dict):
        self.ax[0].cla()  # Clear previous plot
        self.ax[0].set_title("CVM Signal", fontdict={"weight": "bold"})

        if not data_dict:
            self.canvas.draw()
            return 0

        for i, (k, value) in enumerate(data_dict.items()):
            if i >= 30:
                messagebox.showinfo(
                    "Information", "Maximum number of 30 plots reached!"
                )
                break

            t_, amplitude = value
            self.ax[0].plot(t_, amplitude, label=k, color=self.color_dict[i])

        # Set the labels and legends
        self.ax[0].set_xlabel("Time")
        self.ax[0].set_ylabel("Amplitude")
        self.ax[0].legend()

        # Draw the new plot
        self.canvas.draw()


class Event_Org:
    def __init__(self):
        self.track = Track_Event()

    def event_names(self, val):
        event_dict = {
            "outer_ccw": [
                "EAST-STRAIGHT",
                "NORTH-STRAIGHT",
                "CORNER-BUMPS",
                "WEST-STRAIGHT",
            ],
            "Corrugation": ["CORRUGATIONS"],
            "inner_loop": [
                "BELGIAN-BLOCK",
                "NORTH-TURN",
                "BROKEN-CONCRETE",
                "CROSS-DITCHES",
                "POTHOLES",
            ],
            "outer_cw": [
                "WEST-STRAIGHT",
                "CORNER-BUMPS",
                "NORTH-STRAIGHT",
                "EAST-STRAIGHT",
            ],
            "Full_DAQ": [
                "EAST-STRAIGHT",
                "NORTH-STRAIGHT",
                "CORNER-BUMPS",
                "WEST-STRAIGHT",
                "CORRUGATIONS",
                "BELGIAN-BLOCK",
                "NORTH-TURN",
                "BROKEN-CONCRETE",
                "CROSS-DITCHES",
                "POTHOLES",
                "WEST-STRAIGHT2",
                "CORNER-BUMPS2",
                "NORTH-STRAIGHT2",
                "EAST-STRAIGHT2",
            ],
            "Others": self.track.other_events,
            "None": None,
        }
        #################
        print(f"I am inside Event_Org class and val is {val}")
        if val == "Single":
            return "Single"
        elif val not in event_dict:
            return None
        elif val in event_dict.get("Others"):
            return val
        return event_dict.get(val)

    def reorder_time_cvm(self, time_list, start_t):
        t2 = str(time_list[1])
        t1 = str(time_list[0])

        t_delta = Decimal(t2) - Decimal(t1)
        t_delta = float(t_delta)

        new_time = list()

        if start_t == 0:
            start_t = float(Decimal(t1) - Decimal(t1))
        else:
            start_t = start_t + t_delta
        # new_time.append(float(0))
        for i in time_list:
            new_time.append(start_t)
            start_t += t_delta

        return new_time

    def event_seq_creator(self, event_data, event_seq, grid_id, grid_dir):
        print("all events -->", event_data.keys())
        print(event_data)
        print(event_seq)
        print(grid_id, grid_dir)
        if event_seq == "Single" or event_seq in self.track.other_events:
            evt_names = list(event_data.keys())
        else:
            evt_names = self.event_names(event_seq)

        new_data = {grid_id: {}}
        new_data[grid_id] = {grid_dir: {}}
        new_data[grid_id][grid_dir] = {event_seq: {"time": [], "amp": []}}

        t_list = list()
        amp_list = list()

        for ev_count, evt in enumerate(evt_names):
            t_ = event_data.get(evt)[0]
            amp_ = event_data.get(evt)[1]

            t, amp = t_, amp_
            if ev_count == 0:
                t_list.extend(t)
                amp_list.extend(amp)
            if ev_count > 0:
                t = self.reorder_time_cvm(t, t_list[-1])
                t_list.extend(t)
                amp_list.extend(amp)

        new_data[grid_id][grid_dir][event_seq].get("time").extend(t_list)
        new_data[grid_id][grid_dir][event_seq].get("amp").extend(amp_list)
        return np.array(t_list, dtype=np.float64), np.array(amp_list, dtype=np.float64)

    def reorder_one_event(self, xdata, ydata, xmin, xmax, flag_first_event):
        min_x, max_x = min(xdata), max(xdata)
        if xmax - xmin <= (xdata[2] - xdata[1]):
            xmax += 2 * (xdata[2] - xdata[1])
            xmin -= xdata[2] - xdata[1]

        if xmin <= 0:
            xmin = 0
        elif xmin >= max_x:
            index = np.where(xdata == max_x)[0][0]
            xmin = xdata[index - 20]
        else:
            xmin = xmin

        if xmax >= max_x:
            xmax = max_x
        elif xmax <= 0:
            xmax = xdata[20]
        else:
            xmax = xmax

        condition = np.logical_and(xmin < xdata, xdata < xmax)
        # Crop array1 based on the condition
        cropped_array1 = xdata[condition]
        # Apply the same cropping to array2
        cropped_array2 = ydata[condition]

        if flag_first_event:
            cropped_array1 = self.reorder_time_cvm(cropped_array1, 0)

        return cropped_array1, cropped_array2

    def signal_extension(self, event_data, xmin, xmax, event):
        # Retrieve the x and y data from the event data
        signal = event_data.get(event)
        xdata = signal[0]
        ydata = signal[1]

        # Initial debug prints
        increment = xdata[1] - xdata[0]

        if xmax - xmin <= increment:
            return event_data

        xmin = max(0, xmin)
        xmax = min(np.max(xdata), xmax)

        # Select the cropped portion
        condition = (xdata > xmin) & (xdata <= xmax)
        # cropped_time = xdata[condition]
        cropped_amplitude = ydata[condition]

        time_increment = increment
        insert_index = np.searchsorted(xdata, xmax, side="right")

        # insertion_time = xdata[insert_index] if insert_index < len(xdata) else xdata[-1]

        total_time = xdata[-1] + (xmax - xmin)

        new_time = np.arange(0, total_time, time_increment, dtype=np.float64)
        # Concatenate
        extended_amplitude = np.concatenate(
            (ydata[:insert_index], cropped_amplitude, ydata[insert_index + 1 :])
        )

        min_length = min(len(new_time), len(extended_amplitude))

        # Trim `arr1` to match the length of `arr2`
        extended_amplitude = extended_amplitude[:min_length]
        new_time = new_time[:min_length]

        event_data[event] = (new_time, extended_amplitude)

        return event_data

    def event_seq_creator_on_select(
        self, event_data, event_seq, grid_id, grid_dir, event_title_time
    ):
        all_changed_event = list(event_title_time.keys())
        if event_seq == "Single" or event_seq in self.track.other_events:
            evt_names = list(event_data.keys())
        else:
            evt_names = self.event_names(event_seq)

        new_data = {grid_id: {}}
        new_data[grid_id] = {grid_dir: {}}
        new_data[grid_id][grid_dir] = {event_seq: {"time": [], "amp": []}}

        t_list = list()
        amp_list = list()

        for ev_count, evt in enumerate(evt_names):
            if evt in all_changed_event:
                if ev_count == 0:
                    flag_first_event = True
                else:
                    flag_first_event = False
                t_ = event_data.get(evt)[0]
                amp_ = event_data.get(evt)[1]
                xmin, xmax = event_title_time.get(evt)

                t_, amp_ = self.reorder_one_event(
                    t_, amp_, xmin, xmax, flag_first_event
                )
            else:
                t_ = event_data.get(evt)[0]
                amp_ = event_data.get(evt)[1]

            t, amp = t_, amp_
            if ev_count == 0:
                t_list.extend(t)
                amp_list.extend(amp)
            if ev_count > 0:
                t = self.reorder_time_cvm(t, t_list[-1])
                t_list.extend(t)
                amp_list.extend(amp)

        new_data[grid_id][grid_dir][event_seq].get("time").extend(t_list)
        new_data[grid_id][grid_dir][event_seq].get("amp").extend(amp_list)
        return np.array(t_list, dtype=np.float64), np.array(amp_list, dtype=np.float64)

    def crop_signal_func(self, xdata, ydata, xmin, xmax):
        flag_first_event = True
        t, amp = self.reorder_one_event(xdata, ydata, xmin, xmax, flag_first_event)
        return np.array(t, np.float64), np.array(amp, np.float64)


class CvmData:
    def __init__(self, data):
        self.grid_id = None
        self.grid_dir = None
        self.num_of_evnts = None
        self.event_dict = dict()
        self.ev_names = list()
        self.data = data
        self.get_grid_id()

    def get_grid_id(self):
        if self.data:
            self.grid_id = list(self.data.get("grid").keys())[0]
            self.grid_dir = list(self.data["grid"].get(self.grid_id).keys())[0]
            self.num_of_evnts = len(self.data["grid"][self.grid_id][self.grid_dir])
            self.event_dict = self.data["grid"][self.grid_id][self.grid_dir]
            self.ev_names = list(self.event_dict.keys())

    # def run(self):
    #     self.root.mainloop()


class CVMSignalFrame(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.create_signal_process_tab()
        self.event_org = Event_Org()
        self.reset_buttons = []
        self.test_plot = None
        self.test_sim_plot_data = {}
        self.test_original = None

        self.shared_data = DataSingelton()

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=10)
        self.columnconfigure(0, weight=10)

        self.func_help = Help_utils()

        # print(self.track.other_events)

    def create_signal_process_tab(self):
        # Process frame create frames
        self.help_frame = tk.Frame(self)
        self.event_comb_frame = tk.Frame(self)
        self.event_single_frame = tk.Frame(self)

        self.track = Track_Event()
        self.extra_evs = self.track.other_events
        self.extra_evs.insert(0, "None")

        # Process frame grid all frames
        self.help_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.event_comb_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.event_single_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.var_dropdown = tk.StringVar()

        # Create help frame widgets
        self.help_button = tk.Button(
            self.help_frame, text="Help signal", command=self.help_toplevel
        )
        self.var = tk.StringVar(value="None")
        self.checkbox_outer_ccw = tk.Radiobutton(
            self.help_frame,
            text="outer ccw",
            value="outer_ccw",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.checkbox_corrugation = tk.Radiobutton(
            self.help_frame,
            text="Corrugation",
            value="Corrugation",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.checkbox_inner_loop = tk.Radiobutton(
            self.help_frame,
            text="inner loop",
            value="inner_loop",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.checkbox_outer_cw = tk.Radiobutton(
            self.help_frame,
            text="outer cw",
            value="outer_cw",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.checkbox_full_daq = tk.Radiobutton(
            self.help_frame,
            text="full_DAQ",
            value="Full_DAQ",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.checkbox_single = tk.Radiobutton(
            self.help_frame,
            text="Single",
            value="Single",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.checkbox_none = tk.Radiobutton(
            self.help_frame,
            text="None",
            value="None",
            variable=self.var,
            command=lambda: self.check_one_chbox(None),
        )
        self.dropdown = ttk.Combobox(
            self.help_frame,
            textvariable=self.var_dropdown,
            values=self.track.other_events,
            state="readonly",
        )

        ########### PAIRING FUNCTIONALITY

        # Set default value
        self.dropdown.current(0)

        # Bind selection change
        self.dropdown.bind("<<ComboboxSelected>>", self.check_one_chbox)

        self.help_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.checkbox_outer_ccw.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.checkbox_corrugation.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.checkbox_inner_loop.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.checkbox_outer_cw.grid(row=0, column=4, padx=10, pady=10, sticky="ew")
        self.checkbox_full_daq.grid(row=0, column=5, padx=10, pady=10, sticky="ew")
        self.checkbox_single.grid(row=0, column=6, padx=10, pady=10, sticky="ew")
        self.checkbox_none.grid(row=0, column=7, padx=10, pady=10, sticky="ew")
        self.dropdown.grid(row=0, column=8, padx=10, pady=10, sticky="ew")

        # set configure
        self.event_comb_frame.rowconfigure(0, weight=1)
        self.event_comb_frame.rowconfigure(1, weight=1)
        self.event_comb_frame.columnconfigure(0, weight=1)

        # simulation event in single plot
        self.fig_event = plt.figure(figsize=(10, 3))
        # self.fig_event = plt.figure()
        self.canvas = FigureCanvasTkAgg(self.fig_event, master=self.event_comb_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="snew")

        # set configure
        self.event_single_frame.rowconfigure(0, weight=1)
        self.event_single_frame.columnconfigure(0, weight=1)

        #### figure to combine all signals
        self.fig_combine, self.ax_sim_test = plt.subplots(figsize=(10, 3))
        self.canvas_combine = FigureCanvasTkAgg(
            self.fig_combine, master=self.event_single_frame
        )
        self.canvas_combine.get_tk_widget().grid(row=0, column=0, sticky="snew")

        (self.sim_line,) = self.ax_sim_test.plot(
            [], [], label="Combine simulation", color="b"
        )
        (self.test_line,) = self.ax_sim_test.plot([], [], label="Test", color="r")
        self.ax_sim_test.set_title("Combine simulation versus Test")
        self.ax_sim_test.legend()
        # Create a checkbox
        self.var_test_plot = tk.BooleanVar()
        self.checkbox_csv_show = tk.Checkbutton(
            self.event_single_frame,
            text="Show/Hide test curve",
            variable=self.var_test_plot,
            command=self.plot_test_curve,
        )
        ######################################
        #### Create crop test and redo test
        self.crop_test_buttn = tk.Button(
            self.event_single_frame,
            text="Crop test",
            command=lambda ax=self.ax_sim_test: self.croptest(),
        )
        self.crop_test_buttn.grid(row=1, column=0, padx=180, pady=5, sticky="w")
        self.undo_test_buttn = tk.Button(
            self.event_single_frame,
            text="Undo test",
            command=lambda ax=self.ax_sim_test: self.undotest(),
        )
        self.undo_test_buttn.grid(row=1, column=0, padx=280, pady=5, sticky="w")

        # self.appl_crop_buttn = tk.Button(self.event_single_frame, text="Apply crop to all test", command=lambda ax=self.ax_sim_test: self.apply_crop())
        # self.appl_crop_buttn.grid(row=1, column=0, padx=380, pady=5, sticky="w")
        ##################################
        self.checkbox_csv_show.grid(row=1, column=0, padx=1, pady=1, sticky="w")
        self.var_sim_plot = tk.BooleanVar()
        self.checkbox_sim_hide = tk.Checkbutton(
            self.event_single_frame,
            text="Hide Simulation plot",
            variable=self.var_sim_plot,
            command=self.hide_sim_plot,
        )
        self.checkbox_sim_hide.grid(row=1, column=0, padx=1, pady=1, sticky="e")

        # Create a SpanSelector for sim test plot widget
        self.span_sim_test = SpanSelector(
            self.ax_sim_test,
            lambda xmin, xmax, ax=self.ax_sim_test: self.onselect_sim_plot(
                ax, xmin, xmax
            ),
            "horizontal",
            useblit=True,
        )

        # Create a reset button for this plot and position it in the second row
        self.reset_button_sim_test = tk.Button(
            self.event_single_frame,
            text="Reset View",
            command=lambda ax=self.ax_sim_test: self.reset_view_sim_test(ax),
        )
        self.reset_button_sim_test.grid(
            row=1, column=0, padx=5, pady=5, sticky="n"
        )  # Use grid for positioning
        self.sim_test_original_limit = [((0, 0), (0, 0)), ((0, 0), (0, 0))]

    # def apply_crop(self):
    #     pass

    def croptest(self):
        x = self.ax_sim_test.get_xlim()
        xmin, xmax = x
        print(xmin, xmax)
        print("self.test_original --> ", self.test_original)
        if self.test_original:
            selected_csv = self.test_original
            csv_title = list(selected_csv.keys())[0]
            time_csv = list(selected_csv.values())[0][0]
            amp_csv = list(selected_csv.values())[0][1]

            x_new, y_new = self.event_org.crop_signal_func(
                time_csv, amp_csv, xmin, xmax
            )
            x_test_lim = (min(x_new), max(x_new))
            y_test_lim = (min(y_new), max(y_new))
            print("x test limit -->", x_test_lim)
            print("y test limit -->", y_test_lim)
            self.test_line.set_data(x_new, y_new)
            self.sim_test_original_limit.pop(1)
            self.sim_test_original_limit.insert(1, (x_test_lim, y_test_lim))

            self.ax_sim_test.relim()  # Recalculate limits
            self.ax_sim_test.autoscale_view()

            limits = self.func_help.find_max_min_lim(self.sim_test_original_limit)
            original_xlim, original_ylim = limits
            self.ax_sim_test.set_xlim(original_xlim)
            self.ax_sim_test.set_ylim(original_ylim)

            ##3 update the main test data
            select_csv_copy = {}
            select_csv_copy[csv_title] = x_new, y_new
            self.shared_data.test_data = {"csv": select_csv_copy}

            self.ax_sim_test.figure.canvas.draw()

    def undotest(self):
        if self.test_original:
            print("I am here!!")
            selected_csv = self.test_original
            csv_title = list(selected_csv.keys())[0]
            time_csv = list(selected_csv.values())[0][0]
            amp_csv = list(selected_csv.values())[0][1]
            self.test_line.set_visible(False)
            self.test_line.set_visible(True)
            # self.test_plot = self.ax_row2_evt.plot(time_csv, amp_csv, color='r')
            self.test_line.set_data(time_csv, amp_csv)
            x_test_lim = (min(time_csv), max(time_csv))
            y_test_lim = (min(amp_csv), max(amp_csv))
            self.sim_test_original_limit.pop(1)
            self.sim_test_original_limit.insert(1, (x_test_lim, y_test_lim))

            self.ax_sim_test.relim()  # Recalculate limits
            self.ax_sim_test.autoscale_view()

            limits = self.func_help.find_max_min_lim(self.sim_test_original_limit)
            original_xlim, original_ylim = limits
            self.ax_sim_test.set_xlim(original_xlim)
            self.ax_sim_test.set_ylim(original_ylim)
            self.ax_sim_test.figure.canvas.draw()

            select_csv_copy = {}
            select_csv_copy[csv_title] = time_csv, amp_csv
            self.shared_data.test_data = {"csv": select_csv_copy}

    def hide_sim_plot(self):
        if self.var_sim_plot.get():
            self.sim_test_original_limit.pop(0)
            self.sim_test_original_limit.insert(0, ((0, 0), (0, 0)))
            self.sim_line.set_visible(False)
            self.canvas_combine.draw()
        else:
            x_data = self.sim_line.get_xdata()
            y_data = self.sim_line.get_ydata()
            min_x, max_x = min(x_data), max(x_data)
            min_y, max_y = min(y_data), max(y_data)

            self.sim_line.set_visible(True)
            self.sim_test_original_limit.pop(0)
            self.sim_test_original_limit.insert(0, ((min_x, max_x), (min_y, max_y)))
            self.canvas_combine.draw()

    def plot_test_curve(self):
        # global test_data
        selected_csv = {}
        # self.sim_test_original_limit.insert(1, ((0,0), (0,0)))
        print("self.var_test_plot.get()", self.var_test_plot.get())
        print(self.shared_data.test_data)
        if self.var_test_plot.get():
            if self.shared_data.test_data:
                if self.shared_data.test_data["csv"]:
                    plot_num = len(self.shared_data.test_data.get("csv"))
                    if plot_num != 1:
                        messagebox.showerror("Warning", "Select only one plot")
                        return
                    selected_csv = self.shared_data.test_data.get("csv")
                    self.test_original = selected_csv
                    print(self.shared_data.test_data.get("csv"))
                else:
                    messagebox.showerror("Warning", "Select a curve")
                    return
            else:
                messagebox.showerror("Warning", "No test data available")
                return

            csv_title = list(selected_csv.keys())[0]
            time_csv = list(selected_csv.values())[0][0]
            amp_csv = list(selected_csv.values())[0][1]

            if time_csv[0] == 0:
                self.test_line.set_visible(True)

                # self.test_plot = self.ax_row2_evt.plot(time_csv, amp_csv, color='r')
                self.test_line.set_data(time_csv, amp_csv)

                x_test_lim = (min(time_csv), max(time_csv))
                y_test_lim = (min(amp_csv), max(amp_csv))
                self.sim_test_original_limit.pop(1)
                self.sim_test_original_limit.insert(1, (x_test_lim, y_test_lim))

                self.ax_sim_test.relim()  # Recalculate limits
                self.ax_sim_test.autoscale_view()

                self.canvas_combine.draw()

            else:
                messagebox.showerror("Warning", "Use reorder time to start from 0")

        else:
            self.sim_test_original_limit.pop(1)
            self.sim_test_original_limit.insert(1, ((0, 0), (0, 0)))
            self.test_line.set_visible(False)
            self.canvas_combine.draw()

    def check_one_chbox(self, event=None):
        # global cvm_data
        val = self.var.get()
        val2 = self.var_dropdown.get()
        print("event --> ", self.var_dropdown.get())
        print("vaaal --> ", val)
        if val != "None":
            val = val
        else:
            if val2 != "None":
                val = val2

        print(f"final value of {val}")
        self.shared_data.sim_combin_string = val
        self.val_cvm_plot = val
        # self.fig_event.clf()

        self.event_names = self.event_org.event_names(val)

        if val == "None":
            self.fig_event.clf()

            self.sim_line.set_visible(False)
            self.canvas_combine.draw()
            self.canvas.draw()
            if len(self.reset_buttons) > 0:
                for bn in self.reset_buttons:
                    bn.destroy()
            self.sim_test_original_limit.pop(0)
            self.sim_test_original_limit.insert(0, ((0, 0), (0, 0)))
            return

        cvm_data_obj = CvmData(self.shared_data.cvm_data)
        event_dict = cvm_data_obj.event_dict
        grid_id = cvm_data_obj.grid_id
        grid_dir = cvm_data_obj.grid_dir
        self.ev_names = cvm_data_obj.ev_names  # list of event names from cvm_data
        ev_not_exists = list()

        print("all events", event_dict.keys())

        if val == "Full_DAQ":
            temp_dict = {
                "EAST-STRAIGHT": "EAST-STRAIGHT2",
                "NORTH-STRAIGHT": "NORTH-STRAIGHT2",
                "CORNER-BUMPS": "CORNER-BUMPS2",
                "WEST-STRAIGHT": "WEST-STRAIGHT2",
            }
            for i in temp_dict:
                if i in event_dict:
                    event_dict[temp_dict[i]] = event_dict[i]

        if val == "Single" or val in self.track.other_events and val != "None":
            if len(event_dict) == 1:
                self.event_names = list(event_dict.keys())
                self.seq_t, self.seq_amp = self.event_org.event_seq_creator(
                    event_dict, val, grid_id, grid_dir
                )
                x_test_lim = (min(self.seq_t), max(self.seq_t))
                y_test_lim = (min(self.seq_amp), max(self.seq_amp))
                self.sim_test_original_limit.pop(0)
                self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))
                self.plot_evnt_comb(event_dict, val, grid_id, grid_dir)
            else:
                messagebox.showerror(
                    "Error", f"Select One event\n{len(event_dict)} selected!"
                )
                return

        for i in self.event_names:
            if i not in self.ev_names:
                if not i.endswith("2"):
                    ev_not_exists.append(i)

        if len(ev_not_exists) > 0:
            ev_not_found = ",".join(ev_not_exists)
            messagebox.showerror("Error", f"{ev_not_found}")
            return

        self.event_dict_com_org = {k: event_dict[k] for k in event_dict}

        self.shared_data.sim_combine = {}
        for i in event_dict:
            max_t, min_t = min(event_dict[i][0]), max(event_dict[i][0])
            self.shared_data.sim_combine[i] = max_t, min_t

        self.seq_t, self.seq_amp = self.event_org.event_seq_creator(
            event_dict, val, grid_id, grid_dir
        )

        x_test_lim = (min(self.seq_t), max(self.seq_t))
        y_test_lim = (min(self.seq_amp), max(self.seq_amp))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))
        self.plot_evnt_comb(event_dict, val, grid_id, grid_dir)

    def clear_first_row(self, ax_plot):
        # Clear each subplot in the first row
        for ax in ax_plot:
            ax.cla()  # Clears the content of the axes

    def plot_evnt_comb(self, event_data, val, grid_id, grid_dir):
        if not self.shared_data.cvm_data:
            self.canvas.draw()
            self.canvas_combine.draw()
            return

        cvm_data_obj = CvmData(self.shared_data.cvm_data)
        event_dict = cvm_data_obj.event_dict
        to_plot = [i for i in list(event_dict.keys()) if i in self.event_names]
        event_dict2 = {k: event_dict[k] for k in to_plot}

        first_row_plots = len(self.event_names)
        if len(self.reset_buttons) > 0:
            for bn in self.reset_buttons:
                bn.destroy()

        # Clear the previous figure
        self.fig_event.clf()
        self.ax_row1_evt = []  # Clear previous axes
        self.reset_buttons = []  # Clear previous buttons
        self.span_selectors = []  # Clear previous selectors
        self.original_limits = []  # Clear previous limits
        self.righ_span_selectors = []  # This is for adding signal

        # Create a grid for the plots and buttons
        self.gs_evnt = gridspec.GridSpec(
            1, first_row_plots
        )  # Two rows: one for plots, one for buttons

        ii = 10

        frame_btn = ttk.Frame(self.event_comb_frame)
        frame_btn.grid(row=1, column=0, sticky="ew")

        for index, ev_ in enumerate(self.event_names):
            value = event_dict2.get(ev_)
            key = ev_
            x = value[0]
            y = value[1]
            ax = self.fig_event.add_subplot(
                self.gs_evnt[0, index]
            )  # First row for plots
            ax.plot(x, y)
            ax.set_title(f"{key}", fontsize=8)
            ax.tick_params(axis="both", which="major", labelsize=8)

            # Store the axis for resetting later
            self.ax_row1_evt.append(ax)
            self.original_limits.append((ax.get_xlim(), ax.get_ylim()))

            # Create a SpanSelector widget
            span = SpanSelector(
                ax,
                lambda xmin, xmax, ax=ax: self.onselect(
                    ax, xmin, xmax, val, grid_id, grid_dir, event_data
                ),
                "horizontal",
                useblit=True,
                button=1,
            )
            # Create a SpanSelector widget
            span_right = SpanSelector(
                ax,
                lambda xmin, xmax, ax=ax: self.onselect_right(
                    ax, xmin, xmax, val, grid_id, grid_dir, event_data
                ),
                "horizontal",
                useblit=True,
                button=3,
            )

            self.span_selectors.append(span)
            self.righ_span_selectors.append(span_right)

            # Create a reset button for this plot and position it in the second row
            reset_button = tk.Button(
                frame_btn,
                text="Reset View",
                command=lambda ax=ax: self.reset_view(
                    ax, val, grid_id, grid_dir, event_data
                ),
            )

            if len(self.event_names) <= 5:
                reset_button.pack(side="left", expand=True, padx=100)
            else:
                reset_button.pack(side="left", expand=True, padx=10)

            self.reset_buttons.append(reset_button)

        self.fig_event.tight_layout()
        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t, self.seq_amp)
        self.ax_sim_test.relim()  # Recalculate limits
        self.ax_sim_test.autoscale_view()
        self.fig_combine.tight_layout()
        self.canvas.draw()
        self.canvas_combine.draw()

    def onselect_sim_plot(self, ax, xmin, xmax):
        """Callback function to handle the range selection."""

        ax.set_xlim(xmin, xmax)
        ax.figure.canvas.draw()

    def onselect(self, ax, xmin, xmax, val, grid_id, grid_dir, event_data):
        """Callback function to handle the range selection."""

        ax.set_xlim(xmin, xmax)
        title = ax.get_title()

        ax.figure.canvas.draw()
        if title in self.shared_data.sim_combine:
            self.shared_data.sim_combine[title] = xmin, xmax

        self.seq_t_onselect, self.seq_amp_onselect = (
            self.event_org.event_seq_creator_on_select(
                event_data, val, grid_id, grid_dir, self.shared_data.sim_combine
            )
        )
        x_test_lim = (min(self.seq_t_onselect), max(self.seq_t_onselect))
        y_test_lim = (min(self.seq_amp_onselect), max(self.seq_amp_onselect))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))

        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t_onselect, self.seq_amp_onselect)
        self.ax_sim_test.relim()  # Recalculate limits
        self.ax_sim_test.autoscale_view()

        self.canvas_combine.draw()

    def onselect_right(self, ax, xmin, xmax, val, grid_id, grid_dir, event_data):
        """Callback function to handle the range selection."""

        event = ax.get_title()
        event_data_updated = self.event_org.signal_extension(
            event_data, xmin, xmax, event
        )
        self.shared_data.cvm_data["grid"][grid_id][grid_dir] = event_data_updated
        time_array = event_data_updated[event][0]
        amp_array = event_data_updated[event][1]
        xmax = np.max(time_array)
        xmin = np.min(time_array)
        ymax = np.max(amp_array)
        ymin = np.min(amp_array)

        self.shared_data.sim_combine[event] = xmin, xmax

        # Get the first line in the Axes
        line = ax.get_lines()[0]  # Get the first line in the Axes
        line.set_data(time_array, amp_array)  # Set new data for the li

        ax_index = self.ax_row1_evt.index(ax)
        self.original_limits[ax_index] = ((xmin, xmax), (ymin, ymax))
        ax.set_xlim((xmin, xmax))
        ax.set_ylim((ymin, ymax))
        ax.figure.canvas.draw()

        self.onselect(ax, xmin, xmax, val, grid_id, grid_dir, event_data_updated)

    def reset_view(self, ax, val, grid_id, grid_dir, event_data):
        """Reset the plot to the original view."""
        event = ax.get_title()
        xdata = self.shared_data.cvm_data_copy["grid"][grid_id][grid_dir][event][0]
        ydata = self.shared_data.cvm_data_copy["grid"][grid_id][grid_dir][event][1]
        xmin, xmax = np.min(xdata), np.max(xdata)
        ymin, ymax = np.min(ydata), np.max(ydata)
        ax_index = self.ax_row1_evt.index(ax)

        line = ax.get_lines()[0]  # Get the first line in the Axes
        line.set_data(xdata, ydata)  # Set new data for the line

        self.original_limits[ax_index] = ((xmin, xmax), (ymin, ymax))
        original_xlim, original_ylim = self.original_limits[self.ax_row1_evt.index(ax)]

        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        ax.figure.canvas.draw()

        self.shared_data.cvm_data["grid"][grid_id][grid_dir][event] = (
            self.shared_data.cvm_data_copy["grid"][grid_id][grid_dir][event]
        )

        event_data[event] = self.shared_data.cvm_data_copy["grid"][grid_id][grid_dir][
            event
        ]

        if event in self.shared_data.sim_combine:
            self.shared_data.sim_combine[event] = xmin, xmax

        self.seq_t_onselect, self.seq_amp_onselect = (
            self.event_org.event_seq_creator_on_select(
                event_data, val, grid_id, grid_dir, self.shared_data.sim_combine
            )
        )
        x_test_lim = (min(self.seq_t_onselect), max(self.seq_t_onselect))
        y_test_lim = (min(self.seq_amp_onselect), max(self.seq_amp_onselect))
        self.sim_test_original_limit.pop(0)
        self.sim_test_original_limit.insert(0, (x_test_lim, y_test_lim))

        self.sim_line.set_visible(True)
        self.sim_line.set_data(self.seq_t_onselect, self.seq_amp_onselect)
        self.ax_sim_test.relim()  # Recalculate limits
        self.ax_sim_test.autoscale_view()

        self.canvas_combine.draw()

    @classmethod
    def return_sim_test_plot(cls):
        return cls.sim_line, cls.test_line

    def reset_view_sim_test(self, ax):
        limits = self.func_help.find_max_min_lim(self.sim_test_original_limit)
        original_xlim, original_ylim = limits
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        ax.figure.canvas.draw()

    def help_toplevel(self):
        text = """
outer_ccw":
    'EAST-STRAIGHT', 'NORTH-STRAIGHT', 'CORNER-BUMPS', 'WEST-STRAIGHT'\n
"Corrugation":
    'CORRUGATIONS'\n
'inner_loop':
    'BELGIAN-BLOCK', 'NORTH-TURN', 'BROKEN-CONCRETE', 'CROSS-DITCHES', 'POTHOLES'\n
'outer_cw':
    'WEST-STRAIGHT', 'CORNER-BUMPS',  'NORTH-STRAIGHT', 'EAST-STRAIGHT'"""

        top_level = tk.Toplevel(self.master)
        label = ttk.Label(top_level, text=text)
        label.pack(expand=True, fill="both")


class Help_utils:
    def sample_up(self, amp_array, time_array, time_array_2):
        max_duration = min(time_array[-1], time_array_2[-1])
        target_time = time_array_2[time_array_2 <= max_duration]
        # Interpolation function
        interp_func = interp1d(
            time_array, amp_array, kind="linear", fill_value="extrapolate"
        )

        # Resample the amplitude based on the adjusted target time
        resampled_amplitude = interp_func(target_time)
        return target_time, resampled_amplitude

    def sample_down(self, amplitude_original, downsample_factor):
        # Apply decimation to the amplitude array
        downsampled_amplitude = decimate(amplitude_original, downsample_factor)
        return downsampled_amplitude

    def preprocess_csv(self, f_n):
        self.start_t = time.time()
        """Pre-process CSV to ensure consistent columns before loading with pyarrow."""
        cleaned_lines = []
        with open(f_n, "r") as file:
            # Skip initial metadata rows
            for _ in range(2):
                next(file)

            # Extract the header row
            headers = next(file).strip().split(",")
            expected_columns = len(
                headers
            )  # Determine the number of columns dynamically

            # Skip four more rows of additional metadata
            for _ in range(4):
                next(file)

            # Append header row to the cleaned lines
            cleaned_lines.append(",".join(headers))

            # Append only lines with the expected number of columns
            for line in file:
                values = line.strip().split(",")
                if len(values) == expected_columns:
                    cleaned_lines.append(line.strip())

        # Write cleaned lines to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w")
        temp_file.write("\n".join(cleaned_lines))
        temp_file.close()
        temp_file.close()
        elapsed_time = time.time() - self.start_t

        return temp_file.name

    def pull_csv_data(self, f_n):
        cleaned_file = self.preprocess_csv(f_n)

        # Step 2: Load the cleaned file with PyArrow
        table = pv.read_csv(cleaned_file)

        # Convert PyArrow Table to Pandas DataFrame for further processing
        data = table.to_pandas()

        # Convert time and amplitude columns to numeric types
        data.iloc[:, 1] = pd.to_numeric(data.iloc[:, 1], errors="coerce")
        data.iloc[:, 2:] = data.iloc[:, 2:].apply(pd.to_numeric, errors="coerce")

        # Extract time and amplitude data into a dictionary
        time = data.iloc[:, 1].values
        amplitude_data = data.iloc[:, 2:]
        data_dict = {
            col: {"time": time, "amp": amplitude_data[col].values}
            for col in amplitude_data.columns
        }

        return data_dict

    def check_csv_format(self, f_csv):
        flag = True
        with open(f_csv, "r") as file:
            # cnt = file.read().split('\n')
            cnt = [next(file) for _ in range(12)]

        text = """#HEADER
    #TITLES
     , ,1_Grillesbar_Drv_Ax,all point name
    #UNITS
     , ,g,g,g,g,
    #DATATYPES
    Huge,Double,
    #DATA
    1,90.855000,-0.006422924,actual data,
    """
        for n, l in enumerate(cnt):
            if n == 9:
                break
            if cnt[0].strip() == "#HEADER":
                flag = True
            else:
                flag = False

            if cnt[1].strip() == "#TITLES":
                flag = True
            else:
                flag = False
            if "," in cnt[2]:
                flag = True
            else:
                flag = False
            if cnt[3].strip() == "#UNITS":
                flag = True
            else:
                flag = False
            if "," in cnt[4]:
                flag = True
            else:
                flag = False
            if cnt[5].strip() == "#DATATYPES":
                flag = True
            else:
                flag = False

            if "," in cnt[6]:
                flag = True
            else:
                flag = False
            if cnt[7].strip() == "#DATA":
                flag = True
            else:
                flag = False
        return flag, text

    def find_max_min_lim(self, list_max_min):
        max_t = 0
        min_t = 0
        max_amp = 0
        min_amp = 0
        for i in list_max_min:
            for number, j in enumerate(i):
                if number == 0:
                    min_, max_ = j
                    if min_ <= min_t:
                        min_t = min_
                    if max_ >= max_t:
                        max_t = max_
                elif number % 2 == 0:
                    min_, max_ = j
                    if min_ <= min_t:
                        min_t = min_
                    if max_ >= max_t:
                        max_t = max_
                else:
                    min_, max_ = j
                    if min_ <= min_amp:
                        min_amp = min_
                    if max_ >= max_amp:
                        max_amp = max_
        lim = (min_t, max_t), (min_amp, max_amp)
        return lim

    def calc_psd(self, seq_t, seq_amp):
        t_increment = seq_t[2] - seq_t[1]
        fs = 1 / t_increment  # Sample frequency
        frequencies_test, psd_test = welch(seq_amp, fs=fs, nperseg=1024)
        return frequencies_test, psd_test

    def calc_lcr(self, seq_t, seq_amp):
        """Calculate level crossing rate for a signal."""
        num_levels = 500
        # reference_level_type = 'mean'

        # Calculate reference level and levels
        # reference_level = np.mean(seq_amp) if reference_level_type == 'mean' else 0
        levels = np.linspace(np.min(seq_amp), np.max(seq_amp), num_levels)

        # Calculate crossings using a vectorized approach
        signal_shifted = seq_amp[1:]  # signal from second element to end
        signal_original = seq_amp[:-1]  # signal from start to second last element
        crossings = np.zeros(num_levels, dtype=int)

        # Vectorized comparison to check for crossings
        for i, level in enumerate(levels):
            crossings[i] = np.sum(
                ((signal_original < level) & (signal_shifted >= level))
                | ((signal_original > level) & (signal_shifted <= level))
            )
        return dict(zip(levels, crossings))

    def calc_max_min_rms(self, signal):
        # signal = np.asarray(signal)
        max_value = np.max(signal)
        min_value = np.min(signal)
        rms_value = np.sqrt(np.mean(signal**2))
        return max_value, min_value, rms_value

    def rainflow_counting(self, signal):
        # Function to perform rainflow counting on a signal
        ranges = []
        peaks, _ = find_peaks(signal)
        troughs, _ = find_peaks(-signal)
        all_extrema = np.sort(np.concatenate((peaks, troughs)))
        for i in range(len(all_extrema) - 1):
            for j in range(i + 2, len(all_extrema), 2):
                range_value = abs(signal[all_extrema[j]] - signal[all_extrema[i]])
                ranges.append(range_value)
                break
        return np.array(ranges)

    def calculate_damage(self, signal):
        m = 5  # Slope of S-N curve
        S1 = 1000  # S-N curve intersects S-axis at 1000
        N_eq = 2_000_000  # Number of cycles for equivalent load calculation

        # Perform rainflow counting
        ranges = self.rainflow_counting(signal)

        # Calculate damage using Palmgren-Miner rule
        damage = 0
        for stress_range in ranges:
            N_i = (S1 / stress_range) ** m  # S-N curve equation
            damage += 1 / N_i
        return damage

    def equivalent_stress(self, damage):
        # Parameters
        m = 5  # Slope of S-N curve
        S1 = 1000  # S-N curve intersects S-axis at 1000
        N_eq = 2_000_000  # Number of cycles for equivalent load calculation
        # Calculate equivalent stress for N_eq cycles
        return S1 * (damage / N_eq) ** (1 / m)

    def low_high_pass_filter(self, time_array, signal, cutoff, b_type):
        dt = time_array[2] - time_array[1]
        fs = 1 / dt
        if b_type == "low":
            y = self.apply_lowpass_filter(signal, cutoff, fs, b_type, order=5)
        else:
            y = self.apply_highpass_filter(signal, cutoff, fs, b_type, order=5)
        return y

    def band_pass_filter_func(self, time_array, signal, low_f, high_f):
        dt = time_array[2] - time_array[1]
        fs = 1 / dt
        y1_ = self.apply_lowpass_filter(signal, low_f, fs, "low", order=5)
        y2_ = self.apply_highpass_filter(y1_, high_f, fs, "high", order=5)
        return y2_

    def butter_lowpass_highpass(self, cutoff, fs, b_type, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype=b_type, analog=False)
        return b, a

    def apply_lowpass_filter(self, data, cutoff, fs, b_type, order=5):
        b, a = self.butter_lowpass_highpass(cutoff, fs, b_type, order=order)
        y = filtfilt(b, a, data)  # Apply the filter to the signal
        return y

    def apply_highpass_filter(self, data, cutoff, fs, b_type, order=5):
        b, a = self.butter_lowpass_highpass(cutoff, fs, b_type, order=order)
        y = filtfilt(b, a, data)  # Apply the filter to the signal
        return y


class ConvertSignalFrame(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.utils = Utils()
        self.help_func = Help_utils()
        self.csv_dict = {}

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.convert_frame = tk.Frame(self)
        self.convert_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.convert_frame.rowconfigure(0, weight=1)
        self.convert_frame.rowconfigure(1, weight=1)
        self.convert_frame.columnconfigure(0, weight=1)

        self.rsp_frame = tk.Frame(self.convert_frame)
        self.rsp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.csv_frame = tk.Frame(self.convert_frame)
        self.csv_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Folder Selection (Top Frame CSV)
        self.label_rsp = tk.Label(self.rsp_frame, text="Selected Folder path:")
        self.label_rsp.pack(side=tk.LEFT, padx=5)

        #### For R files
        self.line_edit_rsp = tk.Entry(self.rsp_frame, width=70)
        self.line_edit_rsp.pack(side=tk.LEFT, padx=5)
        self.button_rsp = tk.Button(
            self.rsp_frame,
            text="Select RSP or S3T to convert to CSV",
            command=self.select_folder,
        )
        self.button_rsp.pack(side=tk.LEFT, padx=5)

        self.s3t_var = tk.BooleanVar()
        # Create a checkbox
        self.checkbox_s3t = tk.Checkbutton(
            self.rsp_frame, text="s3t (rsp if not selected)", variable=self.s3t_var
        )
        self.checkbox_s3t.pack(side=tk.LEFT, padx=5)

        #### convert csv to R file structure
        self.button_csv = tk.Button(
            self.csv_frame,
            text="Convert CSV to R file structure",
            command=self.select_csv_file,
        )
        self.button_csv.grid(row=0, column=0)
        self.line_edit_csv = tk.Entry(self.csv_frame, width=70)
        self.line_edit_csv.grid(row=0, column=1)
        self.label_csv_com = tk.Label(self.csv_frame, text="CSV File comppatible: ? ")
        self.label_csv_com.grid(row=1, column=0)

        # Combo box creation
        self.combo_config = ttk.Combobox(
            self.csv_frame, values=["Loaded", "Unloaded", "Bobtail"]
        )
        self.combo_config.grid(row=2, column=0)

        self.combo_track = ttk.Combobox(
            self.csv_frame,
            values=[
                "EAST-STRAIGHT",
                "NORTH-STRAIGHT",
                "CORNER-BUMPS",
                "WEST-STRAIGHT",
                "CORRUGATIONS",
                "BELGIAN-BLOCK",
                "NORTH-TURN",
                "BROKEN-CONCRETE",
                "CROSS-DITCHES",
                "POTHOLES",
            ],
        )
        self.combo_track.grid(row=2, column=1)
        self.button_save_r = tk.Button(
            self.csv_frame, text="Save R File structure", command=self.save_r_struct
        )
        self.button_save_r.grid(row=3, column=0)

    def create_folder_if_not_exists(self, folder_path):
        # Check if the folder exists; if not, create it

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            print("folder exists!!")

    def create_r_file(self, folder_save):
        dir_dict = {"_Ax": "_T1", "_Ay": "_T2", "_Az": "_T3"}
        # to capture this pattern ---> ACCE51790001_T3
        for k in self.csv_dict:
            print(k)
            for k1 in dir_dict:
                if k1 not in k.strip():
                    l = k
                    l1 = l + ".R"
                    f_name = os.path.join(folder_save, l1)
                    with open(f_name, "w") as f:
                        for i, j in zip(
                            self.csv_dict[k].get("time"), self.csv_dict[k].get("amp")
                        ):
                            line = f"{i}\t{j}"
                            f.write(line)
                            f.write("\n")
                else:
                    l = k.replace(k1, dir_dict.get(k1))
                    l1 = "ACCE_" + l + ".R"
                    f_name = os.path.join(folder_save, l1)
                    with open(f_name, "w") as f:
                        for i, j in zip(
                            self.csv_dict[k].get("time"), self.csv_dict[k].get("amp")
                        ):
                            line = f"{i}\t{j}"
                            f.write(line)
                            f.write("\n")

    def save_r_struct(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        print(folder_path)
        selected_config = self.combo_config.get()
        selected_track = self.combo_track.get()

        abs_path_config = os.path.join(folder_path, selected_config)

        if len(selected_config) == 0 or len(selected_track) == 0:
            messagebox.showerror("Error", "select config and track first!")
            return

        self.create_folder_if_not_exists(abs_path_config)
        abs_track_path = os.path.join(abs_path_config, selected_track)
        self.create_folder_if_not_exists(abs_track_path)
        print("I am here")
        self.create_r_file(abs_track_path)

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv")],
            multiple=False,
        )
        if file_path:
            self.line_edit_csv.delete(0, tk.END)
            self.line_edit_csv.insert(0, file_path)
            flag, text = self.help_func.check_csv_format(file_path)

        if flag:
            self.label_csv_com.config(text="CSV File comppatible: OK! ")
            self.csv_dict = self.help_func.pull_csv_data(file_path)

        else:
            self.label_csv_com.config(text="CSV File comppatible: WRONG! ")
            messagebox.showerror("Error incompatible CSV", text)
            return 0

    # Function that runs the task and updates the progress bar

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.line_edit_rsp.delete(0, tk.END)
            self.line_edit_rsp.insert(0, folder_path)
            if self.s3t_var.get():
                file_type = "*.s3t"
            else:
                file_type = "*.[rR][sS][pP]"

            self.file_type = file_type
            self.start_progress_window(file_type, folder_path)

    def run_task(self, progress_var, progress_window, file_type, folder_path, label):
        # Simulating a task with a loop, updating the progress bar
        rsp_files = self.utils.create_csv_from_s3t_rsp(folder_path, file_type)
        """Convert RSP files to CSV format."""
        if not rsp_files:
            messagebox.showerror("Error", "No such file type found!")
            return None

        shutil.copy("/nobackup/vol01/a504696/rsp_to_csv/rsp_2_csv.flo", folder_path)
        flo_path = os.path.abspath("rsp_2_csv.flo")
        cc_com = 0
        for n, rsp in enumerate(rsp_files):
            label.config(text=f"{n + 1} file of {len(rsp_files)}")
            self.utils.process_rsp_file(rsp, flo_path)
            cc_com += (100 / len(rsp_files)) - 1

            # progress_var.set(1)
            progress_var.set(cc_com)  # Update progress bar value
            progress_window.update_idletasks()  # Force the GUI to update

        # Close the progress window after task is completed
        # progress_window.destroy()
        label.config(text=f"All {len(rsp_files)} files are converted!")
        time.sleep(0.5)
        progress_var.set(100)
        progress_window.after(1000, progress_window.destroy)

    # Function to open a new window with the progress bar
    def start_progress_window(self, file_type, folder_path):
        # Create a new window for the progress bar
        progress_window = tk.Toplevel(self.master.root)
        # progress_window.title("Task in Progress")

        # Create a label to show progress text
        label = ttk.Label(progress_window, text="Task is in progress, please wait...")
        label.pack(pady=10)

        # Create a variable to store the progress value
        progress_var = tk.IntVar()

        # Create the progress bar widget
        progress_bar = ttk.Progressbar(
            progress_window, length=300, variable=progress_var, maximum=100
        )
        progress_bar.pack(pady=10)

        # Run the task in a separate thread to avoid freezing the UI
        threading.Thread(
            target=self.run_task,
            args=(progress_var, progress_window, file_type, folder_path, label),
            daemon=True,
        ).start()
        # task_thread.start()


class TestVsSim(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.notebook = notebook

        # Initialize shared objects and variables
        self.setup_shared_objects()
        self.setup_variables()

        # Setup UI and plots
        self.setup_ui()
        self.setup_plots()
        self.setup_listboxes()

    def setup_shared_objects(self):
        # Initialize shared objects here
        self.event_org = Event_Org()
        self.shared_data = DataSingelton()
        self.func_help = Help_utils()
        self.event_obj = Event_Org()

    def setup_variables(self):
        # Initialize any variables or shared data here
        self.sim_lines = {}
        self.test_lines = {}
        self.flag_reset_sim = True
        self.flag_reset_test = True
        self.apply_sim = False
        self.apply_test = False
        self.modified_sim_data = {}
        self.modified_test_data = {}
        self.annotations = []

        self.crop_dict = {"test": {}, "sim": {}}
        self.crop_lim = [0, 0]

        self.curve_sim_name = "None"
        self.curve_test_name = "None"

        # Initialize text object lists
        self.text_objects_sim = []  # List to store text objects for simulation plots
        self.text_objects_test = []  # List to store text objects for test plots

        # Initialize original limits
        self.sim_test_original_limit = [
            None,
            None,
        ]  # Initialize limits for simulation and test

        # Variables for filters and analysis settings
        self.low_filter_val = tk.DoubleVar(value=90)
        self.high_filter_val = tk.DoubleVar(value=5)
        self.low_pass_band = tk.DoubleVar(value=90)
        self.high_pass_band = tk.DoubleVar(value=5)
        self.slop_sn = tk.DoubleVar(value=5)
        self.sn_intersect = tk.IntVar(value=1000)
        self.number_of_cycle = tk.IntVar(value=2_000_000)
        self.psd_x_limit = tk.IntVar(value=40)
        self.up_sample_freq = tk.IntVar(value=1000)
        self.down_sample_freq = tk.IntVar(value=2)

        self.data_func = {
            "Low pass filter": {"Low_pass": self.low_filter_val},
            "High pass filter": {"High_pass": self.high_filter_val},
            "Band pass filter": {
                "Low_pass_band": self.low_pass_band,
                "High_pass_band": self.high_pass_band,
            },
            "Damage": {
                "Slope_sn": self.slop_sn,
                "sn_intersect": self.sn_intersect,
                "number_of_cycle": self.number_of_cycle,
            },
            "PSD": {"psd_x_axis": self.psd_x_limit},
            "up-sample": {"freq_up_sample": self.up_sample_freq},
            "down-sample": {"freq_down_sample": self.down_sample_freq},
        }

        self.sim_test_original_limit = [
            ((0, 1), (0, 1)),  # Placeholder limits for self.ax_sim_test
            ((0.1, 50), (1e-10, 1)),  # Placeholder limits for self.ax_analyse[0] (PSD)
            ((1, 1000), (0, 10)),  # Placeholder limits for self.ax_analyse[1] (LCR)
        ]

    def setup_ui(self):
        # Set up the frames and layout
        self.analysis_frame = tk.Frame(self, relief=tk.SOLID, borderwidth=1)
        self.analysis_frame.grid(row=0, column=0, sticky="w")

        self.plot_frame = ttk.Frame(self)
        self.plot_frame.grid(row=0, column=1, sticky="nsew")
        self.analyse_plot_frame = ttk.Frame(self)
        self.analyse_plot_frame.grid(row=1, column=1, sticky="nsew")

        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)
        self.analyse_plot_frame.rowconfigure(0, weight=1)
        self.analyse_plot_frame.columnconfigure(0, weight=1)

    def setup_plots(self):
        # Create figures and axes
        self.fig_analyse, self.ax_analyse = plt.subplots(1, 2, figsize=(10, 3))
        self.fig_combine, self.ax_sim_test = plt.subplots(figsize=(10, 3))

        # Set up canvas for the figures
        self.canvas_analyse = FigureCanvasTkAgg(
            self.fig_analyse, master=self.analyse_plot_frame
        )
        self.canvas_analyse.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.canvas_combine = FigureCanvasTkAgg(
            self.fig_combine, master=self.plot_frame
        )
        self.canvas_combine.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Connect Matplotlib events
        self.cid_hover = self.canvas_combine.mpl_connect(
            "motion_notify_event", self.on_hover
        )
        self.cid_click = self.canvas_combine.mpl_connect(
            "button_press_event", self.on_click
        )

        # Configure plots
        self.fig_analyse.tight_layout(pad=2.0)
        self.fig_combine.tight_layout()

        # Set up lines, titles, and legends
        self.setup_lines()
        self.setup_titles()
        self.setup_legends()
        self.setup_buttons()
        self.config_span()

    def config_span(self):
        self.span_combine = SpanSelector(
            self.ax_sim_test,
            lambda xmin, xmax, ax=self.ax_sim_test: self.onselect_sim_plot(
                ax, xmin, xmax
            ),
            "horizontal",
            useblit=True,
        )
        self.span_psd = SpanSelector(
            self.ax_analyse[0],
            lambda xmin, xmax, ax=self.ax_analyse[0]: self.onselect_psd_plot(
                ax, xmin, xmax
            ),
            "horizontal",
            useblit=True,
        )
        self.span_lcr = SpanSelector(
            self.ax_analyse[1],
            lambda xmin, xmax, ax=self.ax_analyse[1]: self.onselect_lcr_plot(
                ax, xmin, xmax
            ),
            "horizontal",
            useblit=True,
        )

        self.span_combine.set_active(False)  # Initially inactive
        self.shift_pressed = False

        # Bind key press and release events to control activation
        self.cid_key_press = self.canvas_combine.mpl_connect(
            "key_press_event", self.on_key_press
        )
        self.cid_key_release = self.canvas_combine.mpl_connect(
            "key_release_event", self.on_key_release
        )

    def setup_lines(self):
        # Set up the lines for each plot and store them in dictionaries for easy access
        (self.sim_lines["psd"],) = self.ax_analyse[0].semilogy(
            [], [], label="psd sim", color="b"
        )
        (self.test_lines["psd"],) = self.ax_analyse[0].semilogy(
            [], [], label="psd test", color="r"
        )

        (self.sim_lines["lcr"],) = self.ax_analyse[1].plot(
            [], [], label="lcr sim", color="b"
        )
        (self.test_lines["lcr"],) = self.ax_analyse[1].plot(
            [], [], label="lcr test", color="r"
        )

        (self.sim_lines["combine"],) = self.ax_sim_test.plot(
            [], [], label="Combine simulation", color="b"
        )
        (self.test_lines["combine"],) = self.ax_sim_test.plot(
            [], [], label="Test", color="r"
        )

    def setup_titles(self):
        # Set titles for axes
        self.ax_analyse[0].set_title("PSD", fontdict={"weight": "bold"})
        self.ax_analyse[1].set_title("Level Crossing", fontdict={"weight": "bold"})
        self.ax_sim_test.set_title("Sim versus Test", fontdict={"weight": "bold"})

    def setup_legends(self):
        # Set up legends where needed
        self.ax_analyse[0].legend()
        self.ax_analyse[1].legend()
        self.ax_sim_test.legend(loc="upper center")

    def setup_buttons(self):
        # Create update and reset buttons for each plot
        self.update_btn = tk.Button(
            self.plot_frame,
            text="Update",
            command=lambda: self.update_plot(True, "both"),
        )
        self.update_btn.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.reset_button_sim_test = tk.Button(
            self.plot_frame,
            text="Reset View",
            command=lambda: self.reset_view_sim_test(self.ax_sim_test),
        )
        self.reset_button_sim_test.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.crop_button_sim_test = tk.Button(
            self.plot_frame, text="Crop Signal", command=self.crop_plot
        )
        self.crop_button_sim_test.grid(row=1, column=0, padx=145, pady=5, sticky="w")

        self.reset_button_psd = tk.Button(
            self.analyse_plot_frame,
            text="Reset View",
            command=lambda: self.reset_view_psd_plot(self.ax_analyse[0]),
        )
        self.reset_button_psd.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.reset_button_lcr = tk.Button(
            self.analyse_plot_frame,
            text="Reset View",
            command=lambda: self.reset_view_sim_test(self.ax_analyse[1]),
        )
        self.reset_button_lcr.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    def setup_listboxes(self):
        # Frame for the listboxes
        self.left_frame = tk.Frame(self.analysis_frame)
        self.right_frame = tk.Frame(self.analysis_frame)
        self.left_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1)

        # Label for the listboxes
        label_sim_test = tk.Label(
            self.left_frame, text="Curves available", font=("Arial", 10)
        )
        label_sim_test.grid(row=0, column=0)

        # Listbox for curve selection
        self.curve_listbox = tk.Listbox(
            self.left_frame, exportselection=False, height=3
        )
        self.curve_listbox.grid(row=1, column=0)

        # Listbox for analysis functions
        self.analysis_listbox = tk.Listbox(self.left_frame, exportselection=False)
        self.analysis_listbox.grid(row=2, column=0)
        self.analysis_listbox.bind("<<ListboxSelect>>", self.on_listbox_analysis_select)

        # Insert items into the listboxes
        self.all_analyse_funcs = [
            "Low pass filter",
            "High pass filter",
            "Band pass filter",
            "PSD",
            "Damage",
            "up-sample",
            "down-sample",
            "None",
        ]
        self.insert_to_listbox()

        # Info frame for the selected analysis options
        self.analyse_info_frame = tk.Frame(self.right_frame, width=50)
        self.analyse_info_frame.grid(row=0, column=0)

    def on_key_press(self, event):
        # Activate SpanSelector only when Shift is pressed
        print("shift clicked!!!!!")
        if event.key == "shift":
            self.span_combine.set_active(True)
            self.shift_pressed = True  # Track Shift state

    def on_key_release(self, event):
        print("shift released clicked!!!!!")
        # Deactivate SpanSelector when Shift is released
        if event.key == "shift":
            self.span_combine.set_active(False)
            self.shift_pressed = False  # Reset Shift state

    def on_hover(self, event):
        if event.inaxes:
            for line_key, line in {**self.sim_lines, **self.test_lines}.items():
                for x, y in zip(line.get_xdata(), line.get_ydata()):
                    if abs(event.xdata - x) < 0.1 and abs(event.ydata - y) < 0.1:
                        self.master.master.title(
                            f"x: {x:.2f}, y: {y:.2f}, Line: {line_key}"
                        )
                        return

    def get_closeest_val(self, xdata, ydata, val):
        close_index = np.abs(xdata - val).argmin()
        x_targ = xdata[close_index]
        y_targ = ydata[close_index]
        return x_targ, y_targ

    def put_annot(self, event, x_targ, y_targ, col):
        if not any(
            annotation.xy == (x_targ, y_targ) for annotation in self.annotations
        ):
            annotation = event.inaxes.annotate(
                f"({x_targ:.2f}, {y_targ:.2f})",
                xy=(x_targ, y_targ),
                textcoords="offset points",
                xytext=(5, 5),
                ha="center",
                color=col,
            )
            self.annotations.append(annotation)
            self.canvas_combine.draw()

    def remove_annot(self, x_targ, y_targ):
        for annotation in self.annotations:
            if annotation.xy == (x_targ, y_targ):
                annotation.remove()
                self.annotations.remove(annotation)
                self.canvas_combine.draw()
                break

    def on_click(self, event):
        thresh = 0.01
        if event.inaxes:
            sim_l = self.sim_lines["combine"]
            test_l = self.test_lines["combine"]
            xdata, ydata = sim_l.get_xdata(), sim_l.get_ydata()
            xdata_test, ydata_test = test_l.get_xdata(), test_l.get_ydata()
            x_event, y_event = event.xdata, event.ydata
            large_distance = 1e10
            distance_sim, distance_test = 1e11, 1e12
            if len(xdata) > 0:
                x_targ_sim, y_targ_sim = self.get_closeest_val(
                    xdata, ydata, event.xdata
                )
                distance_sim = np.sqrt(
                    (x_event - x_targ_sim) ** 2 + (y_event - y_targ_sim) ** 2
                )

            if len(xdata_test) > 0:
                x_targ_test, y_targ_test = self.get_closeest_val(
                    xdata_test, ydata_test, event.xdata
                )
                distance_test = np.sqrt(
                    (x_event - x_targ_test) ** 2 + (y_event - y_targ_test) ** 2
                )

            if event.button == 1 and not self.shift_pressed:
                if np.abs(distance_sim - distance_test) <= thresh:
                    self.put_annot(event, x_targ_sim, y_targ_sim, "blue")
                    self.put_annot(event, x_targ_test, y_targ_test, "red")
                elif distance_sim < distance_test and distance_sim < large_distance:
                    self.put_annot(event, x_targ_sim, y_targ_sim, "blue")
                elif distance_sim > distance_test and distance_test < large_distance:
                    self.put_annot(event, x_targ_test, y_targ_test, "red")

            elif (
                event.button == 3 and not self.shift_pressed
            ):  # Right-click to remove specific annotation
                if np.abs(distance_sim - distance_test) <= thresh:
                    self.remove_annot(x_targ_sim, y_targ_sim)
                    self.remove_annot(x_targ_test, y_targ_test)
                elif distance_sim < distance_test and distance_sim < large_distance:
                    self.remove_annot(x_targ_sim, y_targ_sim)
                elif distance_sim > distance_test and distance_test < large_distance:
                    self.remove_annot(x_targ_test, y_targ_test)

    def crop_plot(self):
        if self.crop_lim[0] == 0 and self.crop_lim[1] == 0:
            messagebox.showwarning("warning", "Nothing to crop!")
            return

        elif self.crop_lim[1] - self.crop_lim[0] < 3:
            messagebox.showwarning("warning", "Too short to crop!")
            return

        x_sim_data = self.sim_lines.get("combine").get_xdata()
        y_sim_data = self.sim_lines.get("combine").get_ydata()
        x_test_data = self.test_lines.get("combine").get_xdata()
        y_test_data = self.test_lines.get("combine").get_ydata()

        xmin = self.crop_lim[0]
        xmax = self.crop_lim[1]
        if len(x_sim_data) > 20:
            x_new, y_new = self.event_obj.crop_signal_func(
                x_sim_data, y_sim_data, xmin, xmax
            )
            self.modified_sim_data["time"] = x_new
            self.modified_sim_data["amp"] = y_new
            self.update_plot(False, "sim")
            self.flag_reset_sim = False

            self.draw_simulation_plot(x_new, y_new, self.curve_sim_name)

        if len(x_test_data) > 20:
            x_new, y_new = self.event_obj.crop_signal_func(
                x_test_data, y_test_data, xmin, xmax
            )
            self.modified_test_data["time"] = x_new
            self.modified_test_data["amp"] = y_new
            self.update_plot(False, "test")
            self.flag_reset_test = False
            self.plot_test(x_new, y_new)

    def insert_to_listbox(self):
        # Insert items into the listboxes
        for func in self.all_analyse_funcs:
            self.analysis_listbox.insert(tk.END, func)

    def onselect_sim_plot(self, ax, xmin, xmax):
        """Callback function to handle the range selection."""
        ax.set_xlim(xmin, xmax)

        self.crop_lim = [xmin, xmax]
        ax.figure.canvas.draw()

    def onselect_psd_plot(self, ax, xmin, xmax):
        """Callback function to handle the range selection."""
        ax.set_xlim(xmin, xmax)
        ax.figure.canvas.draw()

    def onselect_lcr_plot(self, ax, xmin, xmax):
        """Callback function to handle the range selection."""
        ax.set_xlim(xmin, xmax)
        ax.figure.canvas.draw()

    def get_list_box_curve(self):
        selected_curve_index = self.curve_listbox.curselection()
        if len(selected_curve_index) == 0:
            return None

        selected_curve = self.curve_listbox.get(selected_curve_index[0])
        return selected_curve

    def undo_func(self):
        selected_curve = self.get_list_box_curve()
        if selected_curve == None:
            messagebox.showerror("Warning", "Select a curve from listBox")
            return

        if ":" in selected_curve:
            self.flag_reset_sim = True
        elif len(selected_curve) > 1 and ":" not in selected_curve:
            self.flag_reset_test = True

        self.update_plot(True, "sim" if self.apply_sim else "test")

    def apply_func(self):
        # Initialize flags for applying simulations and tests
        self.apply_sim = False

        # Get the selected function from the listbox
        selected_func_index = self.analysis_listbox.curselection()
        if not selected_func_index:
            messagebox.showerror("Warning", "No function selected in the listbox.")
            return

        selected_func = self.all_analyse_funcs[selected_func_index[0]]
        selected_curve = self.get_list_box_curve()

        # Check if a curve is selected
        if selected_curve == "None" or not selected_curve:
            messagebox.showerror("Warning", "Select a curve from the listbox.")
            return

        # Handle simulation curve selection
        if ":" in selected_curve:
            self.apply_sim = True

            if self.flag_reset_sim:
                # Initialize simulation data if reset flag is set
                time_array, signal, curve_sim_name = self.calc_cvm_time_amp()
                self.modified_sim_data["time"] = time_array
                self.modified_sim_data["amp"] = signal
                self.flag_reset_sim = False
            else:
                time_array = self.modified_sim_data.get("time")
                signal = self.modified_sim_data.get("amp")
        else:
            if self.flag_reset_test:
                selected_csv = self.shared_data.test_data.get("csv")
                time_array = list(selected_csv.values())[0][0]
                signal = list(selected_csv.values())[0][1]
                self.modified_test_data["time"] = time_array
                self.modified_test_data["amp"] = signal
                self.flag_reset_test = False
            else:
                time_array = self.modified_test_data.get("time")
                signal = self.modified_test_data.get("amp")

        # Define a mapping for functions to their respective operations
        operations = {
            "Low pass filter": self.apply_low_pass_filter,
            "High pass filter": self.apply_high_pass_filter,
            "Band pass filter": self.apply_band_pass_filter,
            "Damage": self.apply_damage,
            "up-sample": self.apply_up_sample,
            "down-sample": self.apply_down_sample,
        }

        # Apply the selected function if it exists in the operations mapping
        operation = operations.get(selected_func)
        if operation:
            operation(time_array, signal)
        else:
            messagebox.showerror(
                "Error", f"No valid operation found for: {selected_func}"
            )

        self.flag_reset = False

    def update_the_modify_dict(self, t, y):
        if self.apply_sim:
            self.modified_sim_data["amp"] = y
            self.modified_sim_data["time"] = t
        else:
            self.modified_test_data["amp"] = y
            self.modified_test_data["time"] = t

    def apply_low_pass_filter(self, time_array, signal):
        """Apply low pass filter and update the plot."""
        low_pass = self.low_filter_val.get()
        cutoff = low_pass
        y = self.func_help.low_high_pass_filter(time_array, signal, cutoff, "low")
        self.update_the_modify_dict(time_array, y)
        self.update_plot(False, "sim" if self.apply_sim else "test")
        if self.apply_sim:
            self.draw_simulation_plot(time_array, y, self.curve_sim_name)
        else:
            self.plot_test(time_array, y)

    def apply_high_pass_filter(self, time_array, signal):
        """Apply high pass filter and update the plot."""
        high_pass = self.high_filter_val.get()
        cutoff = high_pass
        y = self.func_help.low_high_pass_filter(time_array, signal, cutoff, "high")
        self.update_the_modify_dict(time_array, y)
        self.update_plot(False, "sim" if self.apply_sim else "test")
        if self.apply_sim:
            self.draw_simulation_plot(time_array, y, self.curve_sim_name)
        else:
            self.plot_test(time_array, y)

    def apply_band_pass_filter(self, time_array, signal):
        """Apply band pass filter and update the plot."""
        low_pass_band = self.low_pass_band.get()
        high_pass_band = self.high_pass_band.get()

        y = self.func_help.band_pass_filter_func(
            time_array, signal, low_pass_band, high_pass_band
        )

        self.update_the_modify_dict(time_array, y)
        self.update_plot(False, "sim" if self.apply_sim else "test")
        if self.apply_sim:
            self.draw_simulation_plot(time_array, y, self.curve_sim_name)
        else:
            self.plot_test(time_array, y)
        # Add functionality for band pass filtering here
        # e.g., y = self.func_help.band_pass_filter(time_array, signal, low_pass_band, high_pass_band)
        # self.draw_simulation_plot(time_array, y, self.curve_sim_name)

    def apply_damage(self, time_array, signal):
        """Apply damage analysis and output parameters."""
        sn_slop = self.slop_sn.get()
        sn_intersect = self.sn_intersect.get()
        sn_cycle = self.number_of_cycle.get()
        # Add functionality for damage analysis here

    def apply_up_sample(self, time_array, signal):
        """Apply up sample on the signal to go from 400 Hz to 1000 Hz ."""
        up_s_fre = self.up_sample_freq.get()
        if self.apply_sim:
            time_array2 = self.test_lines.get("combine").get_xdata()
            max_duration = min(time_array[-1], time_array2[-1])
            target_time = time_array2[time_array2 <= max_duration]
        else:
            time_array2 = self.sim_lines.get("combine").get_xdata()
            max_duration = min(time_array[-1], time_array2[-1])
            target_time = time_array2[time_array2 <= max_duration]
        if len(time_array2) < 20:
            messagebox.showwarning(
                "warning", "you need both test and sim lines to up sample!"
            )
            return

        t_new, y = self.func_help.sample_up(signal, time_array, time_array2)
        # print(f'Band pass filter applied with values:  High={up_s_fre}')
        self.update_the_modify_dict(t_new, y)
        self.update_plot(False, "sim" if self.apply_sim else "test")
        if self.apply_sim:
            self.draw_simulation_plot(t_new, y, self.curve_sim_name)
        else:
            self.plot_test(t_new, y)

        # Add functionality for damage analysis here

    def apply_down_sample(self, time_array, signal):
        """Apply down sample on the signal to go from 1000 Hz to 400 Hz ."""
        downsample_factor = self.down_sample_freq.get()
        if self.apply_sim:
            time_array2 = self.test_lines.get("combine").get_xdata()
            if len(time_array2) < 20:
                messagebox.showwarning(
                    "warning", "you need both test and sim lines to up sample!"
                )
                return
            max_duration = min(time_array[-1], time_array2[-1])
            target_time = time_array2[time_array2 <= max_duration]
        else:
            time_array2 = self.sim_lines.get("combine").get_xdata()
            if len(time_array2) < 20:
                messagebox.showwarning(
                    "warning", "you need both test and sim lines to up sample!"
                )
                return
            max_duration = min(time_array[-1], time_array2[-1])
            target_time = time_array2[time_array2 <= max_duration]

        t_new, y = self.func_help.sample_up(signal, time_array, time_array2)
        # print(f'Band pass filter applied with values:  High={downsample_factor}')
        self.update_the_modify_dict(t_new, y)
        self.update_plot(False, "sim" if self.apply_sim else "test")
        if self.apply_sim:
            self.draw_simulation_plot(t_new, y, self.curve_sim_name)
        else:
            self.plot_test(t_new, y)

    def create_analysis_detail(self):
        # Clear the previous analysis info frame
        self.analyse_info_frame.destroy()
        self.analyse_info_frame = tk.Frame(self.right_frame, width=50)
        self.analyse_info_frame.grid(row=0, column=0)

        # Get the selected function name from the listbox
        selected_func_index = self.analysis_listbox.curselection()
        func_name = (
            self.all_analyse_funcs[selected_func_index[0]]
            if selected_func_index
            else None
        )

        # print('inside create_analysis_detail : ', func_name)

        # Create and place the Apply and Reset buttons
        self.apply_btn = tk.Button(
            self.analyse_info_frame, text="Apply", command=self.apply_func
        )
        self.apply_btn.grid(
            row=10, column=0, padx=5, pady=5, sticky="w"
        )  # Use grid for positioning

        self.undo_btn = tk.Button(
            self.analyse_info_frame, text="Reset Curve", command=self.undo_func
        )
        self.undo_btn.grid(row=10, column=1, padx=5, pady=5, sticky="w")

        # print('func_name -->', func_name)

        # Set up entry fields based on the selected function
        if func_name:
            self.create_input_fields(func_name)

    def create_input_fields(self, func_name):
        """Create input fields based on the selected function."""
        # Mapping of function names to their respective labels and variables
        input_fields = {
            "Low pass filter": ("Freq Low pass", self.low_filter_val),
            "High pass filter": ("Freq High Pass", self.high_filter_val),
            "PSD": ("PSD X axis Limit", self.psd_x_limit),
            "Band pass filter": [
                ("Low Pass Value", self.low_pass_band),
                ("High Pass Value", self.high_pass_band),
            ],
            "Damage": [
                ("Slop S-N", self.slop_sn),
                ("S-N intersect", self.sn_intersect),
                ("Number of Cycle", self.number_of_cycle),
            ],
            "up-sample": ("freq up sample", self.up_sample_freq),
            "down-sample": ("freq down sample", self.down_sample_freq),
        }

        # Create labels and entries based on the selected function
        if func_name in input_fields:
            if isinstance(input_fields[func_name], list):
                for idx, (label_text, var) in enumerate(input_fields[func_name]):
                    tk.Label(
                        self.analyse_info_frame, text=label_text, font=("Arial", 10)
                    ).grid(row=idx, column=0, sticky="w")
                    entry = tk.Entry(
                        self.analyse_info_frame, textvariable=var, width=10
                    )
                    entry.grid(row=idx, column=1, sticky="w")
            else:
                label_text, var = input_fields[func_name]
                tk.Label(
                    self.analyse_info_frame, text=label_text, font=("Arial", 10)
                ).grid(row=0, column=0, sticky="w")
                entry = tk.Entry(self.analyse_info_frame, textvariable=var, width=10)
                entry.grid(row=0, column=1, sticky="w")
        else:
            self.analyse_info_frame.destroy()

    def on_listbox_analysis_select(self, event):
        self.create_analysis_detail()

    def reset_view_psd_plot(self, ax):
        """Reset the view of the given axis based on the data currently plotted."""
        # Find all the lines in the given axis
        lines = [line for line in ax.get_lines() if line.get_visible()]

        if lines:
            # Determine the min and max values for x and y based on all visible lines
            all_x_data = []
            all_y_data = []

            for line in lines:
                x_data, y_data = line.get_data()
                if len(x_data) > 0 and len(y_data) > 0:
                    all_x_data.extend(x_data)
                    all_y_data.extend(y_data)
            all_x_data = np.array(all_x_data)
            all_y_data = np.array(all_y_data)

            sorted_indices = np.argsort(all_x_data)

            # Sort both arrays using the sorted indices of array1
            array1_sorted = all_x_data[sorted_indices]
            array2_sorted = all_y_data[sorted_indices]

            condition = array1_sorted < 40
            y_filtered = array2_sorted[condition]
            x_filtered = array1_sorted[condition]
            # Set axis limits based on the combined data from all lines
            if len(all_x_data) > 0 and len(all_y_data) > 0:
                x_min, x_max = min(x_filtered), max(x_filtered)
                y_min, y_max = min(y_filtered), max(y_filtered)

                y_range = y_max - y_min
                y_margin = 0.1 * y_range
                # y_min -= y_margin
                # y_max += y_margin

                if y_min <= 0:
                    y_min == 1e-10
                if y_max <= 0:
                    y_max == 1e-10

                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max)
                # yticks = np.linspace(y_min, y_max, num=5)
                # ax.set_yticks(yticks)
        # Redraw the figure
        ax.figure.canvas.draw()

    def reset_view_sim_test(self, ax):
        """Reset the view of the given axis based on the data currently plotted."""
        # Find all the lines in the given axis
        lines = [line for line in ax.get_lines() if line.get_visible()]

        if lines:
            # Determine the min and max values for x and y based on all visible lines
            all_x_data = []
            all_y_data = []

            for line in lines:
                x_data, y_data = line.get_data()
                if len(x_data) > 0 and len(y_data) > 0:
                    all_x_data.extend(x_data)
                    all_y_data.extend(y_data)

            # Set axis limits based on the combined data from all lines
            if all_x_data and all_y_data:
                x_min, x_max = min(all_x_data), max(all_x_data)
                y_min, y_max = min(all_y_data), max(all_y_data)

                y_range = y_max - y_min
                y_margin = 0.1 * y_range
                y_min -= y_margin
                y_max += y_margin

                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max)

        # Redraw the figure
        ax.figure.canvas.draw()

    def check_test_plot(self):
        selected_csv = {}
        if self.shared_data.test_data:
            if self.shared_data.test_data["csv"]:
                plot_num = len(self.shared_data.test_data.get("csv"))
                if plot_num != 1:
                    messagebox.showerror("Warning", "Select only one plot")
                    return
                selected_csv = self.shared_data.test_data.get("csv")
                csv_title = list(selected_csv.keys())[0]
                time_csv = list(selected_csv.values())[0][0]
                amp_csv = list(selected_csv.values())[0][1]

                self.curve_test_name = csv_title
                self.plot_test(time_csv, amp_csv)

            else:
                messagebox.showerror("Warning", "Select a curve")
                return
        else:
            messagebox.showerror("Warning", "No test data available")
            return

    def plot_test(self, time_csv, amp_csv):
        """Plot the test signal and relevant metrics."""

        # Check if the first time value is zero
        if time_csv[0] == 0:
            # Get the line corresponding to the test signal from the dictionary
            self.test_lines["combine"].set_data(
                time_csv, amp_csv
            )  # Use a default key or adjust based on your needs

            self.test_lines["combine"].set_label("Test")
            self.test_lines["combine"].set_color("r")
            self.test_lines["combine"].set_visible(True)
            # Set x and y limits based on the data
            x_test_lim = (min(time_csv), max(time_csv))
            y_test_lim = (min(amp_csv), max(amp_csv))

            self.ax_sim_test.set_xlim(x_test_lim)
            self.ax_sim_test.set_ylim(y_test_lim)

            # Update original limits for the test signal
            self.sim_test_original_limit[1] = (
                x_test_lim,
                y_test_lim,
            )  # Update directly without pop/insertion

            # Calculate metrics
            fre, psd_amp = self.func_help.calc_psd(time_csv, amp_csv)

            crossings = self.func_help.calc_lcr(time_csv, amp_csv)

            damage = self.func_help.calculate_damage(amp_csv)

            max_val, min_val, rms_val = self.func_help.calc_max_min_rms(amp_csv)

            resolution = 1 / (time_csv[1] - time_csv[0])

            # Add metric texts to the plot
            rms_text_test = self.ax_sim_test.text(
                0.05,
                0.90,
                f"Test RMS: {rms_val:.2e}",
                transform=self.ax_sim_test.transAxes,
                fontsize=7,
                verticalalignment="bottom",
                color="r",
                bbox=dict(boxstyle="round", alpha=0.1),
            )

            damage_text_test = self.ax_sim_test.text(
                0.05,
                0.01,
                f"Test Damage: {damage:.2e}",
                transform=self.ax_sim_test.transAxes,
                fontsize=7,
                verticalalignment="bottom",
                color="r",
                bbox=dict(boxstyle="round", alpha=0.1),
            )

            res_text_test = self.ax_sim_test.text(
                0.50,
                0.03,
                f"Test Freq: {resolution:.1f}",
                transform=self.ax_sim_test.transAxes,
                fontsize=7,
                verticalalignment="bottom",
                color="r",
                bbox=dict(boxstyle="round", alpha=0.1),
            )

            # Append text objects to the list for later clearing if needed
            self.text_objects_test.extend(
                [damage_text_test, rms_text_test, res_text_test]
            )

            # print('inside test plot function', self.text_objects_test)

            self.ax_sim_test.legend(loc="upper center")
            # Refresh the canvas
            self.canvas_combine.draw()

            # Draw additional plots for LCR and PSD
            self.draw_lcr(crossings, "test")
            self.draw_psd(fre, psd_amp, "test")

        else:
            messagebox.showerror("Warning", "Reorder the Time for test signal")
            return

    def insert_first_item(self, listbox, new_item, item_index):
        listbox.insert(item_index, new_item)

    def calc_cvm_time_amp(self):
        cvm_data_obj = CvmData(self.shared_data.cvm_data)
        event_dict = cvm_data_obj.event_dict
        grid_id = cvm_data_obj.grid_id
        grid_dir = cvm_data_obj.grid_dir
        curve_sim_name = f"{grid_id}:{grid_dir}:{self.shared_data.sim_combin_string}"

        seq_t, seq_amp = self.event_org.event_seq_creator_on_select(
            event_dict,
            self.shared_data.sim_combin_string,
            grid_id,
            grid_dir,
            self.shared_data.sim_combine,
        )

        return seq_t, seq_amp, curve_sim_name

    def check_sim_plot(self):
        # print('self.shared_data.sim_combin_string,', self.shared_data.sim_combin_string)
        if not self.shared_data.cvm_data or self.shared_data.sim_combin_string == "":
            messagebox.showerror("Warning", "No Simulation data available")
            return
        seq_t, seq_amp, curve_sim_name = self.calc_cvm_time_amp()
        self.draw_simulation_plot(seq_t, seq_amp, curve_sim_name)

    def draw_simulation_plot(self, seq_t, seq_amp, curve_sim_name):
        """Draw the simulation plot and relevant metrics."""
        self.curve_sim_name = curve_sim_name
        self.sim_lines["combine"].set_data(seq_t, seq_amp)
        self.sim_lines["combine"].set_label("Combine simulation")
        self.sim_lines["combine"].set_color("b")
        self.sim_lines["combine"].set_visible(True)

        # Set axis limits based on the data
        self.set_axis_limits(seq_t, seq_amp)

        # Store original limits for future reference
        self.update_simulation_limits(seq_t, seq_amp)

        # Calculate metrics
        fre, psd_amp = self.func_help.calc_psd(seq_t, seq_amp)
        crossings = self.func_help.calc_lcr(seq_t, seq_amp)
        damage = self.func_help.calculate_damage(seq_amp)
        max_val, min_val, rms_val = self.func_help.calc_max_min_rms(seq_amp)
        resolution = 1 / (seq_t[1] - seq_t[0])
        # Add metric texts to the plot

        self.ax_sim_test.legend(loc="upper center")
        # Draw additional plots for LCR and PSD
        self.draw_lcr(crossings, "sim")
        self.draw_psd(fre, psd_amp, "sim")
        self.add_text_metrics(rms_val, damage, resolution)

        # Refresh canvas
        self.canvas_combine.draw()

    def set_axis_limits(self, seq_t, seq_amp):
        """Set x and y limits for the simulation plot."""
        self.ax_sim_test.set_xlim(min(seq_t), max(seq_t))
        self.ax_sim_test.set_ylim(min(seq_amp), max(seq_amp))

    def update_simulation_limits(self, seq_t, seq_amp):
        """Update the original limits for the simulation plot."""
        x_sim_limit = (min(seq_t), max(seq_t))
        y_sim_limit = (min(seq_amp), max(seq_amp))
        self.sim_test_original_limit[0] = (x_sim_limit, y_sim_limit)

    def add_text_metrics(self, rms_val, damage, resolution):
        """Add RMS and Damage metrics to the plot."""
        rms_text_sim = self.ax_sim_test.text(
            0.05,
            0.95,
            f"Sim RMS: {rms_val:.4f}",
            transform=self.ax_sim_test.transAxes,
            fontsize=7,
            verticalalignment="bottom",
            color="b",
            bbox=dict(boxstyle="round", alpha=0.1),
        )

        damage_text_sim = self.ax_sim_test.text(
            0.05,
            0.1,
            f"Sim Damage: {damage:.2e}",
            transform=self.ax_sim_test.transAxes,
            fontsize=7,
            verticalalignment="bottom",
            color="b",
            bbox=dict(boxstyle="round", alpha=0.1),
        )

        res_text_sim = self.ax_sim_test.text(
            0.50,
            0.1,
            f"Sim Freq: {resolution:.1f}",
            transform=self.ax_sim_test.transAxes,
            fontsize=7,
            verticalalignment="bottom",
            color="b",
            bbox=dict(boxstyle="round", alpha=0.1),
        )

        self.text_objects_sim.extend([damage_text_sim, rms_text_sim, res_text_sim])
        # print('inside add_text_metrics', self.text_objects_sim)

    def draw_lcr(self, crossings, value):
        """Draw the level crossing rate plot."""
        levels = list(crossings.keys())
        counts = list(crossings.values())

        if value == "sim":
            self.sim_lines.get("lcr").set_data(counts, levels)
            self.sim_lines.get("lcr").set_label("lcr sim")
            self.sim_lines.get("lcr").set_color("b")
            self.sim_lines.get("lcr").set_visible(True)

        else:
            self.test_lines.get("lcr").set_data(counts, levels)
            self.test_lines.get("lcr").set_label("lcr test")
            self.test_lines.get("lcr").set_color("r")
            self.test_lines.get("lcr").set_visible(True)
        # Plot using dictionary to access lines

        self.ax_analyse[1].set_xlim(min(counts), max(counts))
        self.ax_analyse[1].set_ylim(min(levels), max(levels))

        self.ax_analyse[1].set_title("Level Crossing", fontdict={"weight": "bold"})

        self.ax_analyse[1].set_xscale("log")  # Set x-axis to logarithmic scale
        self.ax_analyse[1].set_xlabel("Crossing Count")
        self.ax_analyse[1].set_ylabel("Amplitude")
        self.ax_analyse[1].grid(True)
        self.ax_analyse[1].minorticks_on()
        self.ax_analyse[1].grid(which="both", linestyle="--", linewidth=0.5, alpha=0.7)
        self.ax_analyse[1].grid(which="minor", linestyle=":", linewidth=0.3, alpha=0.5)
        self.ax_analyse[1].legend(loc="upper right")

        self.canvas_analyse.draw()

    def draw_psd(self, freq, psd_amp, value):
        """Draw the power spectral density plot."""

        if value == "sim":
            self.sim_lines.get("psd").set_data(freq, psd_amp)
            self.sim_lines.get("psd").set_label("psd sim")
            self.sim_lines.get("psd").set_color("b")
            self.sim_lines.get("psd").set_visible(True)

        else:
            self.test_lines.get("psd").set_data(freq, psd_amp)
            self.test_lines.get("psd").set_label("psd test")
            self.test_lines.get("psd").set_color("r")
            self.test_lines.get("psd").set_visible(True)

        y_min, y_max = min(psd_amp), max(psd_amp)
        self.ax_analyse[0].set_xlim(-1, 70)
        self.ax_analyse[0].set_ylim(min(psd_amp), max(psd_amp))

        # self.ax_analyse[0].set_xlim(-1, 70)
        self.ax_analyse[0].set_ylim(y_min, y_max)

        # Explicitly set y-ticks to include max value
        y_ticks = np.linspace(
            y_min, y_max, num=5
        )  # Adjust num for more ticks if needed
        y_ticks = np.append(y_ticks, y_max)  # Ensure the max value is included
        y_ticks = np.unique(np.append(y_ticks, y_max))  # Remove duplicates if any

        self.ax_analyse[0].set_xlabel("Frequency (Hz)")
        self.ax_analyse[0].set_ylabel("Power Spectrum Density (V²/Hz)")
        self.ax_analyse[0].set_title("PSD", fontdict={"weight": "bold"})

        # self.ax_analyse[0].yaxis.set_major_locator(MaxNLocator(nbins=5, integer=False, prune='both'))

        self.ax_analyse[0].minorticks_on()
        self.ax_analyse[0].grid(which="both", linestyle="--", linewidth=0.5, alpha=0.7)
        self.ax_analyse[0].grid(which="minor", linestyle=":", linewidth=0.3, alpha=0.5)
        self.ax_analyse[0].legend(loc="lower right")

        self.canvas_analyse.draw()

    def clear_text_list(self, value):
        """Clear text objects based on the specified value."""

        if value == "both":
            for text1 in self.text_objects_sim:
                text1.remove()
            self.text_objects_sim.clear()
            for text1 in self.text_objects_test:
                text1.remove()
            self.text_objects_test.clear()

        elif value == "sim":
            for text in self.text_objects_sim:
                text.remove()
            self.text_objects_sim.clear()
        elif value == "test":
            for text in self.text_objects_test:
                text.remove()
            self.text_objects_test.clear()

    def clear_axis(self, value):
        """Clear the specified axis or both axes."""
        if value == "both":
            # Clear all simulation lines
            for line in self.sim_lines.values():
                line.set_data([], [])
                line.set_label("")

            # Clear all test lines
            for line in self.test_lines.values():
                line.set_data([], [])
                line.set_label("")

        elif value == "sim":
            # print('---- only sim ----')
            # Clear all simulation lines
            for line in self.sim_lines.values():
                line.set_data([], [])
                line.set_label("")

        elif value == "test":
            # print('---- only test ---')
            # Clear all test lines
            for line in self.test_lines.values():
                line.set_data([], [])
                line.set_label("")

    def update_plot(self, flag_first, to_change="both"):
        """Update the plot based on the current state."""

        if to_change == "both":
            self.modified_sim_data = {}
            self.modified_sim_data = {}
            self.flag_reset_sim = True
            self.flag_reset_test = True

        self.clear_text_list(to_change)
        self.clear_axis(to_change)

        if flag_first:
            self.curve_listbox.delete(0, tk.END)
            self.check_sim_plot()
            self.check_test_plot()
            self.insert_first_item(self.curve_listbox, self.curve_sim_name, 0)
            self.insert_first_item(self.curve_listbox, self.curve_test_name, 1)

    def help_toplevel(self):
        self.checkbox_psd_test_var = tk.BooleanVar()
        self.checkbox_lc_test_var = tk.BooleanVar()
        self.checkbox_sig_test_var = tk.BooleanVar()

        top_level = tk.Toplevel(self.master)
        top_level.title("Select Options")
        top_level.geometry("300x200")  # Set initial size

        # Create a frame for better spacing
        frame = tk.Frame(top_level, padx=10, pady=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # Configure row/column weights to expand properly
        top_level.grid_rowconfigure(0, weight=1)
        top_level.grid_columnconfigure(0, weight=1)

        self.checkbox_psd_test = tk.Checkbutton(
            frame,
            text="Save PSD",
            variable=self.checkbox_psd_test_var,
            command=self.test_plots,
        )
        self.checkbox_lc_test = tk.Checkbutton(
            frame,
            text="Save Level Crossing",
            variable=self.checkbox_lc_test_var,
            command=self.test_plots,
        )
        self.checkbox_signal_test = tk.Checkbutton(
            frame,
            text="Save Signal",
            variable=self.checkbox_sig_test_var,
            command=self.test_plots,
        )
        self.checkbox_psd_test.grid(row=0, column=0, sticky="w", pady=5)
        self.checkbox_lc_test.grid(row=1, column=0, sticky="w", pady=5)
        self.checkbox_signal_test.grid(row=2, column=0, sticky="w", pady=5)

        # Create the button
        button = tk.Button(top_level, text="Save file", command=self.save_signal)
        button.grid(row=3, column=0, sticky="ew", pady=5)
        # label = ttk.Label(top_level, text=text)
        # label.pack(expand=True, fill='both')

    def output_simulation(self):
        self.help_toplevel()

    def output_test(self):
        self.help_toplevel()

    def test_plots(self):
        # Get the name of the checkbox that triggered the function
        # checkbox_name = self.master.nametowidget(self.master.call("focus")).cget("text")
        # print(f"Checkbox '{checkbox_name}' was toggled.")
        pass

    def save_signal(self):
        """Retrieve the selected checkboxes and print their names."""
        selected_options = []

        if self.checkbox_psd_test_var.get():
            selected_options.append("Save PSD")
        if self.checkbox_lc_test_var.get():
            selected_options.append("Save Level Crossing")
        if self.checkbox_sig_test_var.get():
            selected_options.append("Save Signal")

        folder_selected = filedialog.askdirectory(title="Select a Folder")
        if folder_selected:  # If a folder is selected, update the entry
            items = self.curve_listbox.get(0, tk.END)

            # Retrieve the first and second item if they exist
            grid_id = items[0].split(":")[0]

            print("folder_selected", folder_selected)
            for k in list(self.sim_lines.keys()):
                sim_l = self.sim_lines[k]

                self.save_csv(folder_selected, f"{str(grid_id)}_{k}", sim_l)

    def save_csv(self, folder_selected, file_name, sim_l):
        xdata, ydata = sim_l.get_xdata(), sim_l.get_ydata()

        # Define CSV file path
        csv_filename = os.path.join(folder_selected, f"{file_name}.csv")

        # Write to CSV file
        with open(csv_filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["X Data", "Y Data"])  # Column headers
            writer.writerows(zip(xdata, ydata))  # Write data row-wise

        print(f"Saved: {csv_filename}")


class SegmenSignalTest:
    def __init__(self):
        # self.shared_data = DataSingelton()
        pass

    # This function takes the signal and determine the boundaries of the signal
    def smoothing_new(self, signal_data, w):
        smoothed = np.convolve(signal_data, np.ones(w), "valid") / w
        padding = np.full(w - 1, smoothed[0])
        return np.concatenate((padding, smoothed))

    # calculate the energy in signal using moving window
    def energy_maximize(self, w, signal, dilate_thresh):
        N = len(signal)
        # dilate threshhold expand the moving window (tolerance level)
        m = w + dilate_thresh + 1
        all_sum, all_dets, all_crange, max_std = [], [], [], []

        for series in range(0, N - m):
            cdil = 1
            std_store, max_std_val, max_crange = [], 0, []
            while cdil < dilate_thresh:
                crange = np.array(range(series - (w + cdil), series + (w + cdil + 1)))
                crange = crange[(crange >= 0) & (crange < N)]
                val = np.abs(np.sum(signal[crange] ** 2))
                std_store.append(val)
                if np.max(std_store) > max_std_val:
                    max_std_val = np.max(std_store)
                    max_crange = signal[crange]
                    cur_crange = crange
                cdil += 1
            all_sum.append(np.abs(np.sum(max_crange)))
            all_dets.append(max_crange)
            all_crange.append(cur_crange)
            max_std.append(np.max(np.abs(std_store)))
        return [all_sum, all_dets, all_crange, max_std]

    # identifing the event based on the energy calculated
    def get_ids(self, maxima_, all_dets, all_crange, power_ratio_thresh):
        event_ids = []
        counted = []
        for idxy, valxy in enumerate(maxima_[:-1]):
            if np.sum(all_dets[maxima_[idxy]] ** 2) > np.sum(
                all_dets[maxima_[idxy + 1]] ** 2
            ):
                intxn = len(
                    set(all_crange[maxima_[idxy]]) & set(all_crange[maxima_[idxy + 1]])
                )
                power_ratio = np.sum(all_dets[maxima_[idxy + 1]] ** 2) * (
                    np.sum(all_dets[maxima_[idxy]] ** 2)
                    / np.sum(all_dets[maxima_[idxy + 1]] ** 2)
                )
                if intxn == 0:
                    event_ids.append(
                        [all_crange[maxima_[idxy]][0], all_crange[maxima_[idxy]][-1]]
                    )
                elif intxn > 0 and power_ratio > power_ratio_thresh:
                    if idxy not in counted:
                        event_ids.append(
                            [
                                all_crange[maxima_[idxy]][0],
                                all_crange[maxima_[idxy + 1]][-1],
                            ]
                        )
                        counted.append(idxy + 1)
        return event_ids

    # this function uses amplitude for determination of the event
    def post_proc(self, event_ids, smoothed_signal, start_end_cut_off_thresh, dy):
        event_ids_final = []
        for ccevent in event_ids:
            cdata = smoothed_signal[ccevent[0] : ccevent[1]]
            mu = np.abs(np.diff(cdata)).mean()
            stdv = np.abs(np.diff(cdata)).std()
            threshv = mu - (start_end_cut_off_thresh * stdv)
            idxs = np.abs(np.diff(cdata)) > threshv
            if np.any(idxs):
                event_start = ccevent[0] + np.where(idxs)[0][0]
                event_end = ccevent[0] + np.where(idxs)[0][-1]
                ac_min, ac_max = cdata.min(), cdata.max()
                if abs(ac_max - ac_min) >= dy:
                    event_ids_final.append([event_start, event_end])
        return event_ids_final

    # run the whole segmentation process
    def run_maximize(
        self,
        signal_data,
        time,
        w,
        dilate_thresh,
        power_ratio_thresh,
        start_end_cut_off_thresh,
        dy,
    ):
        smoothed_signal = self.smoothing_new(signal_data, w)

        [all_sum, all_dets, all_crange, max_std] = self.energy_maximize(
            w, smoothed_signal, dilate_thresh
        )
        maxima_ = argrelextrema(np.array(max_std), np.greater)[0]
        event_ids = self.get_ids(maxima_, all_dets, all_crange, power_ratio_thresh)
        event_ids = self.post_proc(
            event_ids, smoothed_signal, start_end_cut_off_thresh, dy
        )

        segmentation = np.zeros_like(signal_data)
        for start, end in event_ids:
            segmentation[start:end] = 1

        return smoothed_signal, event_ids, segmentation

    # extract the various feature
    def extract_single_feature(self, signal, time_array):
        duration = time_array[-1] - time_array[0]
        features = {
            "duration": duration,
            "mean": np.mean(signal),
            "median": np.median(signal),
            "std": np.std(signal),
            "min": np.min(signal),
            "max": np.max(signal),
            "range": np.max(signal) - np.min(signal),
            "rms": np.sqrt(np.mean(signal**2)),
            "abs_energy": np.sum(signal**2),
            "cv": stats.variation(signal) if np.mean(signal) != 0 else 0,
        }
        return features

    # This function label the feature as event and non-event
    def label_and_extract_features(self, segmentation, signal_data, time):
        changes = np.diff(np.concatenate(([0], segmentation, [0])))
        starts = np.where(changes == 1)[0]
        ends = np.where(changes == -1)[0]

        events = []
        non_events = []

        for i in range(len(starts)):
            event_signal = signal_data[starts[i] : ends[i]]
            event_time = time[starts[i] : ends[i]]
            event_features = self.extract_single_feature(event_signal, event_time)
            event_features["label"] = "event"
            event_features["start_time"] = event_time[0]
            event_features["end_time"] = event_time[-1]
            events.append(event_features)

            if i < len(starts) - 1:
                non_event_signal = signal_data[ends[i] : starts[i + 1]]
                non_event_time = time[ends[i] : starts[i + 1]]
                non_event_features = self.extract_single_feature(
                    non_event_signal, non_event_time
                )
                non_event_features["label"] = "non_event"
                non_event_features["start_time"] = non_event_time[0]
                non_event_features["end_time"] = non_event_time[-1]
                non_events.append(non_event_features)

        return events, non_events

    # This function gather feature that are similar
    # it averages the events so it can find similar events and put them together
    def extract_features(self, segmentation, time):
        changes = np.diff(segmentation)
        event_starts = np.where(changes == 1)[0] + 1
        event_ends = np.where(changes == -1)[0] + 1

        if segmentation[0] == 1:
            event_starts = np.insert(event_starts, 0, 0)
        if segmentation[-1] == 1:
            event_ends = np.append(event_ends, len(segmentation))

        min_length = min(len(event_starts), len(event_ends))
        event_starts = event_starts[:min_length]
        event_ends = event_ends[:min_length]

        event_durations = time[event_ends] - time[event_starts]

        gap_starts = event_ends[:-1]
        gap_ends = event_starts[1:]
        gap_durations = time[gap_ends] - time[gap_starts]

        features = {
            "num_events": len(event_durations),
            "total_time": time[-1] - time[0],
            "event_duration_mean": np.mean(event_durations),
            "event_duration_median": np.median(event_durations),
            "event_duration_std": np.std(event_durations),
            "event_duration_min": np.min(event_durations),
            "event_duration_max": np.max(event_durations),
            "gap_duration_mean": np.mean(gap_durations)
            if len(gap_durations) > 0
            else 0,
            "gap_duration_median": np.median(gap_durations)
            if len(gap_durations) > 0
            else 0,
            "gap_duration_std": np.std(gap_durations) if len(gap_durations) > 0 else 0,
            "gap_duration_min": np.min(gap_durations) if len(gap_durations) > 0 else 0,
            "gap_duration_max": np.max(gap_durations) if len(gap_durations) > 0 else 0,
            "event_frequency": len(event_durations) / (time[-1] - time[0]),
            "event_density": np.sum(event_durations) / (time[-1] - time[0]),
            "event_duration_cv": stats.variation(event_durations),
            "gap_duration_cv": stats.variation(gap_durations)
            if len(gap_durations) > 0
            else 0,
        }

        if len(gap_durations) > 0:
            median_gap = np.median(gap_durations)
            burst_mask = gap_durations < median_gap
            bursts = np.split(burst_mask, np.where(np.diff(burst_mask))[0] + 1)
            bursts = [b for b in bursts if b[0] and len(b) >= 3]

            features["num_bursts"] = len(bursts)
            features["max_burst_length"] = (
                max([len(b) for b in bursts]) if bursts else 0
            )
        else:
            features["num_bursts"] = 0
            features["max_burst_length"] = 0

        return features

    def seg_run(self, data_for_seg):
        time_array = data_for_seg.get("time_csv")
        signal_data = data_for_seg.get("amp_csv")
        # Set parameters for event detection
        w = data_for_seg.get("w")  # Window size for smoothing
        dilate_thresh = data_for_seg.get("dilate_thresh")  # 11-13 #3
        power_ratio_thresh = data_for_seg.get("power_ratio_thresh")  # 0.6 #0.3 #0.5#1
        start_end_cut_off_thresh = data_for_seg.get("cut_off_thresh")  # 14#15
        dy = data_for_seg.get(
            "dy"
        )  # Adjust this based on your signal's characteristics
        time_threshold = data_for_seg.get(
            "time_threshold"
        )  # 1.2 #1.0  # Time threshold for grouping (in seconds

        time_diff = time_array[1] - time_array[0]
        sample_freq = 1 / time_diff

        # Butterworth low-pass filter parameters
        low_order = 8
        low_cut_off_freq = 50

        # Create the low-pass Butterworth filter
        b_low, a_low = butter(
            low_order, low_cut_off_freq / (0.5 * sample_freq), btype="low"
        )

        # Apply forward and backward low-pass filtering
        low_passed_signal = filtfilt(b_low, a_low, signal_data)

        # Butterworth high-pass filter parameters
        high_order = 8
        high_cutoff_freq = 5

        # Create the high-pass Butterworth filter
        b_high, a_high = butter(
            high_order, high_cutoff_freq / (0.5 * sample_freq), btype="high"
        )

        # Apply high-pass filtering on the low-passed signal
        filtered_signal = filtfilt(b_high, a_high, low_passed_signal)

        # Apply smoothing after filtering
        smoothed_signal = self.smoothing_new(filtered_signal, w)

        # Run the event detection
        smoothed_signal, detected_events, original_segmentation = self.run_maximize(
            signal_data,
            time_array,
            w,
            dilate_thresh,
            power_ratio_thresh,
            start_end_cut_off_thresh,
            dy,
        )

        # Group adjacent events based on time difference
        merged_groups = []
        current_group = [detected_events[0]]

        for i in range(1, len(detected_events)):
            if (
                time_array[detected_events[i][0]]
                - time_array[detected_events[i - 1][1]]
                <= time_threshold
            ):
                current_group.append(detected_events[i])
            else:
                merged_groups.append(current_group)
                current_group = [detected_events[i]]
        merged_groups.append(current_group)

        # Create new segmentation based on merged groups
        new_segmentation = np.zeros_like(time_array)
        for group in merged_groups:
            start = group[0][0]
            end = group[-1][-1]
            new_segmentation[start : end + 1] = 1  # +1 to include the end point
        # Label events and non-events, and extract features
        events, non_events = self.label_and_extract_features(
            new_segmentation, signal_data, time_array
        )
        # Create a database of all events and non-events
        all_segments = events + non_events
        # Plot results
        # Extract overall features based on the new grouped segmentation
        overall_features = self.extract_features(new_segmentation, time_array)

        data_to_return = {
            "time_array": time_array,
            "new_segmentation": new_segmentation,
            "non_events": non_events,
            "events": events,
            "overall_features": overall_features,
        }

        return data_to_return


class TestSignalFrame(ttk.Frame):
    def __init__(self, master, notebook):
        super().__init__(master)
        self.master = master
        self.notebook = notebook
        self.ui()
        self.master = master
        self.event_org = Event_Org()
        self.reset_buttons = []
        self.test_plot = None
        self.shared_data = DataSingelton()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.func_help = Help_utils()

    def ui(self):
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.seg_plot_frame = ttk.Frame(self)
        self.seg_plot_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.analysis_frame = tk.Frame(self)
        self.analysis_frame.grid(row=0, column=0, padx=10, pady=10, sticky="snew")

        self.analysis_feat_frame = tk.Frame(self)
        self.analysis_feat_frame.grid(row=1, column=0, padx=10, pady=10, sticky="snew")

        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

        self.seg_plot_frame.rowconfigure(0, weight=1)
        self.seg_plot_frame.columnconfigure(0, weight=1)

        # self.analysis_frame.rowconfigure(0,weight=1)
        self.analysis_frame.columnconfigure(0, weight=1)
        self.analysis_frame.columnconfigure(1, weight=1)

        self.analysis_feat_frame.rowconfigure(1, weight=1)
        self.analysis_feat_frame.columnconfigure(0, weight=1)

        #### figure to combine all signals
        self.fig_combine, self.ax_sim_test = plt.subplots(figsize=(10, 3))
        self.canvas_combine = FigureCanvasTkAgg(
            self.fig_combine, master=self.plot_frame
        )
        self.canvas_combine.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # self.ax_row2_evt = self.fig_combine.add_subplot(2, 1, 1)

        self.fig_segment, self.ax_segment = plt.subplots(figsize=(10, 2))
        self.canvas_segment = FigureCanvasTkAgg(
            self.fig_segment, master=self.seg_plot_frame
        )
        self.canvas_segment.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        (self.test_line,) = self.ax_sim_test.plot([], [], label="Test", color="r")
        self.ax_sim_test.set_title("Test Signal")
        self.ax_sim_test.legend()

        # Create a SpanSelector for sim test plot widget
        self.span_test = SpanSelector(
            self.ax_sim_test,
            lambda xmin, xmax, ax=self.ax_sim_test: self.onselect_sim_plot(
                ax, xmin, xmax
            ),
            "horizontal",
            useblit=True,
        )

        # Create a reset button for this plot and position it in the second row
        self.update_btn = tk.Button(
            self.plot_frame, text="Update", command=self.update_plot
        )
        self.update_btn.grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )  # Use grid for positioning
        # self.sim_test_original_limit= [((0,0),(0,0)),((0,0),(0,0))]
        self.reset_button_sim_test = tk.Button(
            self.plot_frame,
            text="Reset View",
            command=lambda ax=self.ax_sim_test: self.reset_view_sim_test(ax),
        )
        self.reset_button_sim_test.grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )  # Use grid for positioning
        self.sim_test_original_limit = [((0, 0), (0, 0)), ((0, 0), (0, 0))]

        self.segment_btn = tk.Button(
            self.plot_frame, text="Segment Test signal", command=self.segment_test
        )
        self.segment_btn.grid(row=1, column=0, padx=250, pady=5, sticky="w")

        #################
        self.w = tk.IntVar(value=10)
        self.dilate_thresh = tk.IntVar(value=10)
        self.time_threshold = tk.DoubleVar(value=1.4)
        self.dy = tk.DoubleVar(value=1.0)
        self.cut_off_thresh = tk.IntVar(value=12)
        self.power_ratio_thresh = tk.DoubleVar(value=0.6)

        self.label_w = tk.Label(self.analysis_frame, text="Window size for smoothing")
        self.label_dilate_thresh = tk.Label(
            self.analysis_frame, text="dilate threshhold"
        )
        self.label_power_ratio_thresh = tk.Label(
            self.analysis_frame, text="power ratio threshold"
        )
        self.label_cut_off_thresh = tk.Label(
            self.analysis_frame, text="cut off threshold"
        )
        self.label_dy = tk.Label(self.analysis_frame, text="signal's characteristics")
        self.label_time_threshold = tk.Label(self.analysis_frame, text="Time threshold")
        self.entry_w = tk.Entry(self.analysis_frame, textvariable=self.w)
        self.entry_dilate_thresh = tk.Entry(
            self.analysis_frame, textvariable=self.dilate_thresh
        )
        self.entry_power_ratio_thresh = tk.Entry(
            self.analysis_frame, textvariable=self.power_ratio_thresh
        )
        self.entry_cut_off_thresh = tk.Entry(
            self.analysis_frame, textvariable=self.cut_off_thresh
        )
        self.entry_dy = tk.Entry(self.analysis_frame, textvariable=self.dy)
        self.entry_time_thresh = tk.Entry(
            self.analysis_frame, textvariable=self.time_threshold
        )
        ####

        self.label_w.grid(row=0, column=0)
        self.label_dilate_thresh.grid(row=1, column=0)
        self.label_power_ratio_thresh.grid(row=2, column=0)
        self.label_cut_off_thresh.grid(row=3, column=0)
        self.label_dy.grid(row=4, column=0)
        self.label_time_threshold.grid(row=5, column=0)
        self.entry_w.grid(row=0, column=1)
        self.entry_dilate_thresh.grid(row=1, column=1)
        self.entry_power_ratio_thresh.grid(row=2, column=1)
        self.entry_cut_off_thresh.grid(row=3, column=1)
        self.entry_dy.grid(row=4, column=1)
        self.entry_time_thresh.grid(row=5, column=1)
        for child in self.analysis_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.grid(sticky="w")  # Make label sticky to the west
            elif isinstance(child, tk.Entry):
                child.grid(sticky="ew")  # Mak

        label_sim_test = tk.Label(
            self.analysis_feat_frame, text="Feature Information", font=("Arial", 10)
        )

        self.text_widget = tk.Text(self.analysis_feat_frame)

        ## pack left frame widgets
        label_sim_test.grid(row=0, column=0, sticky="n")
        self.text_widget.grid(row=1, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(
            self.analysis_feat_frame, command=self.text_widget.yview
        )
        scrollbar.grid(row=1, column=1, sticky="ns")
        # Configure the Text widget to use the Scrollbar
        self.text_widget.config(yscrollcommand=scrollbar.set)

    def reset_view_sim_test(self, ax):
        limits = self.func_help.find_max_min_lim(self.sim_test_original_limit)
        original_xlim, original_ylim = limits
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        ax.figure.canvas.draw()

    def plot_test(self):
        selected_csv = {}
        if self.shared_data.test_data:
            if self.shared_data.test_data["csv"]:
                plot_num = len(self.shared_data.test_data.get("csv"))
                if plot_num != 1:
                    messagebox.showerror("Warning", "Select only one plot")
                    return
                selected_csv = self.shared_data.test_data.get("csv")
            else:
                messagebox.showerror("Warning", "Select a curve")
                return
        else:
            messagebox.showerror("Warning", "No test data available")
            return

        csv_title = list(selected_csv.keys())[0]
        time_csv = list(selected_csv.values())[0][0]
        amp_csv = list(selected_csv.values())[0][1]

        # if time_csv[0] == 0:
        self.test_line.set_visible(True)
        # self.test_plot = self.ax_row2_evt.plot(time_csv, amp_csv, color='r')
        self.test_line.set_data(time_csv, amp_csv)
        x_test_lim = (min(time_csv), max(time_csv))
        y_test_lim = (min(amp_csv), max(amp_csv))
        self.ax_sim_test.set_xlim(x_test_lim)
        self.ax_sim_test.set_ylim(y_test_lim)
        self.ax_sim_test.relim()  # Recalculate limits
        self.ax_sim_test.autoscale_view()
        self.canvas_combine.draw()

        self.sim_test_original_limit.pop(1)
        self.sim_test_original_limit.insert(1, (x_test_lim, y_test_lim))

        self.fig_combine.tight_layout()
        self.canvas_combine.draw()

    def update_plot(self):
        self.plot_test()

    def onselect_sim_plot(self, ax, xmin, xmax):
        """Callback function to handle the range selection."""
        ax.set_xlim(xmin, xmax)
        ax.figure.canvas.draw()

    def update_text(self, new_text):
        self.text_widget.config(
            state=tk.NORMAL
        )  # Make it editable to clear and update the content
        self.text_widget.delete("1.0", tk.END)  # Clear any existing content
        self.text_widget.insert("1.0", new_text)  # Insert new text at the beginning
        self.text_widget.config(state=tk.DISABLED)

    def draw_segment(self, data_dict):
        # This is the data
        # data_dict = {'new_segmentation':new_segmentation,
        #                   'non_events':non_events, "events":events, 'overall_features':overall_features}
        self.ax_segment
        time_array = data_dict.get("time_array")
        new_segmentation = data_dict.get("new_segmentation")
        events = data_dict.get("events")
        non_events = data_dict.get("non_events")
        # Plot new segmentation with larger bars and labels
        self.ax_segment.fill_between(
            time_array, 0, new_segmentation, step="post", color="blue", alpha=0.7
        )
        self.ax_segment.set_title("Grouped Signal Segmentation")
        self.ax_segment.set_xlabel("Time")
        self.ax_segment.set_ylabel("Event (1) / No Event (0)")
        self.ax_segment.set_ylim(-0.2, 1.2)  # Increased y-axis range for larger bars

        # Add event labels
        for event in events:
            mid_time = (event["start_time"] + event["end_time"]) / 2
            self.ax_segment.text(
                mid_time,
                1.05,
                "E",
                horizontalalignment="center",
                verticalalignment="bottom",
                fontsize=8,
            )

        # Add non-event labels
        for non_event in non_events:
            mid_time = (non_event["start_time"] + non_event["end_time"]) / 2
            self.ax_segment.text(
                mid_time,
                -0.05,
                "NE",
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=8,
            )

        self.fig_segment.tight_layout()
        self.canvas_segment.draw()

    def get_all_parameters(self):
        data = {
            "w": self.w.get(),
            "dilate_thresh": self.dilate_thresh.get(),
            "time_threshold": self.time_threshold.get(),
            "dy": self.dy.get(),
            "cut_off_thresh": self.cut_off_thresh.get(),
            "power_ratio_thresh": self.power_ratio_thresh.get(),
        }

        return data

    def segment_test(self):
        self.ax_segment.clear()
        self.canvas_segment.draw()
        self.seg_signal = SegmenSignalTest()
        selected_csv = self.shared_data.test_data.get("csv")
        csv_title = list(selected_csv.keys())[0]
        time_csv = list(selected_csv.values())[0][0]
        amp_csv = list(selected_csv.values())[0][1]
        data_for_seg = self.get_all_parameters()
        data_for_seg["amp_csv"] = amp_csv
        data_for_seg["time_csv"] = time_csv
        data_dict = self.seg_signal.seg_run(data_for_seg)
        overall_features = data_dict.get("overall_features")
        # Print overall features
        to_put = ""
        for key, value in overall_features.items():
            line = f"{key}: {value}"
            to_put += line
            to_put += "\n"

        self.update_text(to_put)
        self.draw_segment(data_dict)


class ActionFrame(ttk.Frame):
    def __init__(self, master, table, shared_data, **kwargs):
        super().__init__(master, **kwargs)
        self.table = table
        self.pack_opt = dict(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))
        # Actions : buttons
        create_row_button = ttk.Button(self, text="+", command=self.add_row)
        remove_row_button = ttk.Button(self, text="-", command=self.remove_row)
        import_button = ttk.Button(self, text="Import", command=self.import_data)
        export_button = ttk.Button(self, text="Export", command=self.export_data)
        create_row_button.pack(**self.pack_opt)
        remove_row_button.pack(**self.pack_opt)
        import_button.pack(**self.pack_opt)
        export_button.pack(**self.pack_opt)

        self.shared_data = shared_data

        self.track_event = Track_Event()

    def all_ev_comb(self):
        self.all_single_events = [
            "BELGIAN-BLOCK",
            "BRIDGE-CONNECTION",
            "BROKEN-CONCRETE",
            "CHASSIS-TWISTER",
            "CONST-HUMPS",
            "CORNER-BUMPS-CCW",
            "CORNER-BUMPS",
            "CORRUGATIONS",
            "CROSS-ART-RAMP-OPC2",
            "CROSS-ART-RAMP-OPC3",
            "CROSS-DITCHES",
            "EAST-STRAIGHT",
            "EIGHTS",
            "GROUND-TWIST-CW",
            "GROUND-TWIST",
            "I40-RIDE",
            "IL-TEST",
            "INNER-LOOP",
            "NORTH-STRAIGHT",
            "NORTH-TURN",
            "OL-CCW-TEST",
            "OL-HS-CCW-TEST",
            "OL-HS-CW-TEST",
            "POTHOLES",
            "ROLLING-STONES-2",
            "ROLLING-STONES-3",
            "RUT-ROAD",
            "S-TURN",
            "TWISTER-BLOCKS",
            "WEST-STRAIGHT",
        ]
        self.comb_evs = ["outer_ccw", "inner_loop", "outer_cw", "full_daq"]
        self.all_events = self.all_single_events + self.comb_evs

    def get_grid_data(self):
        g_dict = self.shared_data.original_g_dict
        grid_list = list(g_dict.keys())

    def add_row(self):
        # g_dict = self.shared_data.original_g_dict
        # test_dict = self.shared_data.original_test_dict
        g_dict = {
            "1234": {
                "t1": {"test1": {"time": [123], "amp": [123]}},
                "t2": {"test2": {"time": [123], "amp": [123]}},
            }
        }
        test_dict = {"signal 1": {"time": [123], "amp": [123]}}
        if not g_dict or not test_dict:
            messagebox.showinfo("Information", "Read test and simulation data !!")
            return 0

        grid_list = list(g_dict.keys())
        val = [grid_list, [1], [1], [1], [1], [1], [1], [1]]
        row_values = [
            ("combo", grid_list),
            ("combo", [1]),
            ("combo", [1]),
            ("combo", [1]),
            ("entry", []),
            ("entry", []),
            ("entry", []),
            ("entry", []),
        ]
        self.table.create_row(row_values=row_values)

    def remove_row(self):
        self.table.remove_row()

    def import_data(self):
        pass

    def export_data(self):
        pass


class TableFrame(ttk.Frame):
    def __init__(self, master, headers, **kwargs):
        super().__init__(master, **kwargs)

        ### Variables
        self.rows = []
        self.row_frames = []
        self.cells = []
        self.check_all_var = tk.BooleanVar(value=False)
        self.check_row_vars = []
        self.row_number = 0
        # make color dict
        self.headers = headers
        ### Styles
        self.style = ttk.Style()
        self.style.configure("DataFrame.TFrame", background="#708090")
        self.style.configure("HeaderFrame.TFrame", background="#b6927b")
        self.style.configure("RowFrame.TFrame", background="#737373")
        self.style.configure("HighlightRowFrame.TFrame", background="#984936")

        ### Widgets
        # Frames
        self.header_frame = ttk.Frame(self, style="HeaderFrame.TFrame", padding=10)
        self.data_frame = ttk.Frame(self, style="DataFrame.TFrame")

        ### Grid widgets
        self.header_frame.grid(row=0, column=0, sticky="news")
        self.data_frame.grid(row=1, column=0, sticky="news")

        ### Growth size
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)
        # Header Frame
        self.header_frame.rowconfigure(0, weight=1)
        # TODO: Number in the reange should be dynamic which is the len of the header row in total (check, button , etc)
        # FIX: We can achive this by finding out children of the header_frame
        # Well the problem is I would like to give less growth rate for the checkbox as first widget
        # self.header_frame.columnconfigure(0, weight=1)
        for i in range(
            1, len(self.headers) + 1
        ):  # 6 is the len of the columns in header_frame
            self.header_frame.columnconfigure(i, weight=1)
        # Data Frame
        self.data_frame.columnconfigure(0, weight=1)

        self.combo_rows = []

    def create_header(self, headers=[]):
        check_all_button = ttk.Checkbutton(
            self.header_frame, text="", variable=self.check_all_var
        )
        check_all_button["command"] = self.check_all_rows
        check_all_button.grid(sticky="we")

        for index, header in enumerate(headers, 1):
            ttk.Button(self.header_frame, text=header).grid(
                row=0, column=index, sticky="we", padx=5
            )

    def check_all_rows(self):
        # if check_all checkbutton checked
        if self.check_all_var.get():
            for var in self.check_row_vars:
                var.set(True)
            # highlight all rows
            for row in self.row_frames:
                row["style"] = "HighlightRowFrame.TFrame"
        else:
            for var in self.check_row_vars:
                var.set(False)
            # unhighlight
            for row in self.row_frames:
                row["style"] = "RowFrame.TFrame"

    def highlight_row(self, check_var, row):
        if check_var.get():
            row["style"] = "HighlightRowFrame.TFrame"
            return
        row["style"] = "RowFrame.TFrame"

    def populate_combobox_values(self, values):
        pass

    def create_row(self, row_values={}):
        # Row Frame widget
        row_frame = ttk.Frame(self.data_frame, style="RowFrame.TFrame", padding=(5, 10))
        row_frame.grid(
            row=len(self.row_frames), column=0, sticky="news", padx=5, pady=5
        )

        # store row_frame in row_frames list.
        self.row_frames.append(row_frame)

        # Checkbutton var
        check_var = tk.BooleanVar(value=False)
        self.check_row_vars.append(check_var)
        # check_var.set(False)

        # Checkbutton widget
        check_row_button = ttk.Checkbutton(row_frame, text="", variable=check_var)
        check_row_button["command"] = lambda: self.highlight_row(check_var, row_frame)
        check_row_button.grid(row=0, column=0, sticky="we")

        # Widget :: Comboboxes for a row

        # for i, (widget_name,value) in enumerate(row_values,1):
        #     if widget_name == "combo":

        #         combo = ttk.Combobox(row_frame, values=value)
        #         combo.bind("<<ComboboxSelected>>", lambda event: self.on_combo_select(event, combo))
        #         combo.current(0)
        #         combo.grid(row=0, column=i, sticky="we", padx=5)
        #     elif widget_name == "entry":
        #         entry = ttk.Entry(row_frame)
        #         entry.grid(row=0, column=i, sticky="we", padx=5)

        self.comboboxes = {}  # Dictionary to store combobox references

        for i, (widget_name, value) in enumerate(row_values, 1):
            if widget_name == "combo":
                combo = ttk.Combobox(row_frame, values=value)
                combo.bind(
                    "<<ComboboxSelected>>",
                    lambda event, c=combo, idx=i: self.on_combo_select(event, c, idx),
                )
                combo.current(0)
                combo.grid(row=0, column=i, sticky="we", padx=5)

                self.comboboxes[i] = combo  # Store combo with index as key

            elif widget_name == "entry":
                entry = ttk.Entry(row_frame)
                entry.grid(row=0, column=i, sticky="we", padx=5)

        # Growth size same as header growth size
        row_frame.rowconfigure(0, weight=1)
        # Make it dynamic as header_frame needed
        for i in range(1, len(self.headers) + 1):
            row_frame.columnconfigure(i, weight=1)

    # Define an event function
    def on_combo_select(self, event, combo, index):
        print(
            f"Combo {index} selected: {combo.get()}"
        )  # Identify each combobox by index

    def remove_by_index(self, index):
        self.row_frames[index].destroy()
        del self.row_frames[index]
        del self.check_row_vars[index]

    def remove_row(self):
        checked_indeces = sorted(
            [i for i, var in enumerate(self.check_row_vars) if var.get()], reverse=True
        )
        for index in checked_indeces:
            self.remove_by_index(index)
        self.check_all_var.set(False)

        # no row checked: delete last row
        if len(self.row_frames) > 0 and not checked_indeces:
            self.remove_by_index(-1)


class PairingSignalFrame(ttk.Frame):
    def __init__(self, master, notebook, shared_data):
        super().__init__(master)
        self.master = master
        self.notebook = notebook
        self.shared_data = shared_data
        # self.main_frame = tk.Frame(self)
        # self.top_frame = tk.Frame(self.main_frame)
        # self.center_frame = tk.Frame(self.main_frame)
        # self.bottom_frame = tk.Frame(self.main_frame)
        # self.main_frame.grid(row=0,column=0)
        # self.top_frame.grid(row=0,column=0)
        # self.center_frame.grid(row=1,column=0)
        # self.bottom_frame.grid(row=2,column=0)

        self.r_f = R_file("/")
        self.headers = [
            "Grid",
            "Gird dir",
            "Grid event",
            "Test Ch",
            "T-Start",
            "T-End",
            "F-low",
            "F-High",
        ]

        self.table = TableFrame(self, self.headers, padding=10)
        self.table.grid(row=0, column=0, sticky="news")
        self.headers = [
            "Grid",
            "Gird dir",
            "Grid event",
            "Test Ch",
            "T-Start",
            "T-End",
            "F-low",
            "F-High",
        ]
        self.table.create_header(self.headers)

        self.action = ActionFrame(self, self.table, self.shared_data)
        self.action.grid(row=1, column=0, sticky="news")

        # Growth rate
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class NavBar:
    def __init__(self, master):
        self.master = master
        self.menu_bar = Menu(
            self.master, relief="raised"
        )  # Attach the menu to the main Tk instance
        self.master.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0, relief="raised")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.output_menu = Menu(self.menu_bar, tearoff=0, relief="raised")
        self.menu_bar.add_cascade(label="Output", menu=self.output_menu)

    def select_folder(self, readsignal):
        self.file_menu.add_command(
            label="Import Simulation", command=readsignal.select_folder
        )

    def read_csv(self, read_csv):
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Import Test", command=read_csv.select_csv_file
        )

    def out_put_signal_sim(self, out_sim):
        self.output_menu.add_command(
            label="Output sim signal", command=out_sim.output_simulation
        )

    def out_put_signal_test(self, out_test):
        self.file_menu.add_separator()
        self.output_menu.add_command(
            label="Output test signal", command=out_test.output_test
        )

    def add_exit(self):
        self.file_menu.add_separator()  # Optional: Adds a separator line before Exit
        self.file_menu.add_command(label="Exit", command=self.master.quit)


class MainFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Create Notebook (tabs)
        self.navbar = NavBar(master)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.root = master

        # Create Frames for each Tab
        self.read_signal_frame = ReadSignalFrame(self, self.notebook)
        self.cvm_processing_frame = CVMSignalFrame(self, self.notebook)
        self.test_processing_frame = TestSignalFrame(self, self.notebook)
        self.test_vs_sim_frame = TestVsSim(self, self.notebook)
        self.signal_convert_frame = ConvertSignalFrame(self, self.notebook)
        self.signal_pairing_frame = PairingSignalFrame(
            self, self.notebook, self.read_signal_frame.shared_data
        )

        self.notebook.add(self.read_signal_frame, text="Read Signal")
        self.notebook.add(self.cvm_processing_frame, text="Signal Processing")
        self.notebook.add(self.test_processing_frame, text="Test Processing")
        self.notebook.add(self.test_vs_sim_frame, text="Test versus Simulation")
        self.notebook.add(self.signal_convert_frame, text="Signal Conversion")
        self.notebook.add(self.signal_pairing_frame, text="Signal Pairing")

        self.navbar.select_folder(self.read_signal_frame)
        self.navbar.read_csv(self.read_signal_frame)
        self.navbar.add_exit()
        self.navbar.out_put_signal_sim(self.test_vs_sim_frame)
        self.navbar.out_put_signal_test(self.test_vs_sim_frame)

        # config
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.cvm_processing_frame.rowconfigure(0, weight=1)
        self.cvm_processing_frame.columnconfigure(0, weight=1)
        self.test_processing_frame.rowconfigure(0, weight=1)
        self.test_processing_frame.columnconfigure(0, weight=1)
        self.test_processing_frame.columnconfigure(1, weight=1)
        self.test_vs_sim_frame.rowconfigure(0, weight=1)
        self.test_vs_sim_frame.columnconfigure(0, weight=1)
        self.test_vs_sim_frame.columnconfigure(1, weight=1)
        self.signal_convert_frame.rowconfigure(0, weight=1)
        self.signal_convert_frame.columnconfigure(0, weight=1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signal Processing App")
        # self.geometry("1400x900")
        self.main_frame = MainFrame(self)
        self.main_frame.pack(expand=True, fill="both")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.minsize(1200, 800)


if __name__ == "__main__":
    root = App()
    root.mainloop()


# class PairingSignalFrame(ttk.Frame):
#     def __init__(self, master, notebook):
#         super().__init__(master)
#         self.master = master
#         self.notebook = notebook
#         self.main_frame = tk.Frame(self)
#         self.top_frame = tk.Frame(self.main_frame)
#         self.center_frame = tk.Frame(self.main_frame)
#         self.bottom_frame = tk.Frame(self.main_frame)
#         self.main_frame.grid(row=0,column=0)
#         self.top_frame.grid(row=0,column=0)
#         self.center_frame.grid(row=1,column=0)
#         self.bottom_frame.grid(row=2,column=0)

#         self.r_f = R_file("/")

#         self.master = master

#         self.event_org = Event_Org()
#         self.reset_buttons = []
#         self.test_plot = None
#         self.shared_data = DataSingelton()
#         self.rowconfigure(0,weight=1)
#         self.columnconfigure(0,weight=1)

#         self.main_frame.rowconfigure(0,weight=1)
#         self.main_frame.rowconfigure(1,weight=10)
#         self.main_frame.rowconfigure(2,weight=1)

#         self.func_help = Help_utils()
#         self.ui_header()
#         self.ui()
#         self.row_frames = []
#         self.rows_data = []


#     def ui(self):
#         pass

#     def ui_header(self):
#         self.header_frame = tk.Frame(self.top_frame)
#         self.action_frame = tk.Frame(self.top_frame)
#         self.action_frame.grid(row=0,column=0)
#         self.header_frame.grid(row=1,column=0)

#         style = ttk.Style()
#         style.configure("Bold.TButton", font=("Arial", 30, "bold"))

#         self.add_button = ttk.Button(self.action_frame,text='+', style="Bold.TButton", command=self.create_row)
#         self.erase_button = ttk.Button(self.action_frame,text='-',style="Bold.TButton", command=self.erase_row)
#         # Define a custom style for the button


#         self.add_button.grid(row=0,column=0,sticky="w")
#         self.erase_button.grid(row=0,column=1, sticky="e")
#         self.columns_name = ["Sim Grid","Evnet com","Test Sig","Time test starts", "Time test stop","Freq high pass","freq low pass"]
#         self.check_all_var = tk.BooleanVar()

#         # Create Checkbutton and link it to var
#         self.check_all_button = tk.Checkbutton(self.header_frame, text="", variable=self.check_all_var, command=self.check_all)
#         self.check_all_button.grid(row=0,column=0)
#         for n,item in enumerate(self.columns_name):
#             ttk.Button(self.header_frame,text=item).grid(row=0, column=n+1, padx=5,pady=5)


#     def check_all(self):
#         if self.check_all_var.get():
#             print("it is checked")
#         else:
#             print("Unchecked!!!!!!")

#     def create_row(self):
#         row_frame=ttk.Frame(self.center_frame)
#         row_frame.grid(row=len(self.row_frames), column=0)
#         self.row_frames.append(row_frame)
#         drop_down = ttk.Combobox(row_frame)
#         drop_down.grid(row=0,column=0)


#     #####        all_gs = self.r_f.find_all_grid()
#     ####        g_dict_ = self.r_f.grid_track_dict(all_gs)
#     ####        g_dict = self.r_f.convert_to_g(g_dict_)


#         print(self.r_f.find_all_grid())
#     def erase_row(self):
#         if len(self.row_frames) >0:
#             last_frame = self.row_frames.pop()
#             last_frame.destroy()
