# TODO: get_row to get data of a row: get_row(0)
# get_cell_data: to get data of a cell: get_cell_data(row=0, column=2)
# add_hi -> add hihglight for a row
# clear_hi -> clear highlight for a row
# NOTE: future ntoe

import pickle
import tkinter as tk
from tkinter import ttk

from rfile import *


class Data:
    def __init__(self):
        self.ev_not_exist = ""
        self.g_dict = {}
        self.rf = ""
        self.read_rfile("./Data")

    def read_rfile(self, folder_path):
        self.rf = RFile(folder_path)
        flag_daq, ev = self.rf.check_all_dir()
        if flag_daq != True:
            self.ev_not_exist = ev

        all_gs = self.rf.find_all_grid()
        g_dict_ = self.rf.grid_track_dict(all_gs)
        self.g_dict = self.rf.convert_to_g(g_dict_)

    def save_pickle(self):
        # save data(g_dict) as json file
        with open("./sim_data.pickle", "wb") as pickle_file:
            pickle.dump(self.g_dict, pickle_file)
            print("pickle file saved.")

    def load_pickle(self):
        with open("./sim_data.pickle", "rb") as pickle_file:
            pickle.load(pickle_file)

    def prepare_values(self):
        a = []
        b = []
        c = []
        for x, y in self.g_dict.items():
            a.append(x)
            for t, e in y.items():
                b.append(t)
                for z in e:
                    c.append(z)

        return a, b, c

    def prepare_test(self):
        pass




class TableFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ### Variables
        self.rows = []
        self.row_frames = []
        self.cells = []
        self.check_all_var = tk.BooleanVar(value=False)
        self.check_row_vars = []
        self.row_number = 0
        # make color dict

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
        for i in range(1, 6):  # 6 is the len of the columns in header_frame
            self.header_frame.columnconfigure(i, weight=1)
        # Data Frame
        self.data_frame.columnconfigure(0, weight=1)

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

    def create_row(self, row_values=[], widget="Combobox"):
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
        for i, values in enumerate(row_values, 1):
            combo = ttk.Combobox(row_frame, values=values)
            combo.current(0)
            combo.grid(row=0, column=i, sticky="we", padx=5)

        # Growth size same as header growth size
        row_frame.rowconfigure(0, weight=1)
        # Make it dynamic as header_frame needed
        for i in range(1, 6):
            row_frame.columnconfigure(i, weight=1)

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


class ActionFrame(ttk.Frame):
    def __init__(self, master, table, **kwargs):
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

    def add_row(self):
        import random

        # create random data
        val = [
            [random.randrange(100) for i in range(random.randrange(1, 10))]
            for i in range(5)
        ]

        # read rfile
        data = Data()
        a, b, c= data.prepare_values()
        val = [a, b, c, [1, 2, 3], [3, 2, 1]]

        self.table.create_row(row_values=val)

    def remove_row(self):
        self.table.remove_row()

    def import_data(self):
        pass

    def export_data(self):
        pass


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        table = TableFrame(self, padding=10)
        table.grid(row=0, column=0, sticky="news")
        headers = ["hedaer " + str(i) for i in range(1, 6)]
        table.create_header(headers)

        action = ActionFrame(self, table)
        action.grid(row=1, column=0, sticky="news")

        # Growth rate
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Root window options
        self.title("Table Like Widget")
        self.geometry("600x400")

        # Main frame
        mainframe = MainFrame(self, relief="solid", padding=5)
        mainframe.grid(row=0, column=0, sticky="news", padx=20, pady=20)

        # Growth rate
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
