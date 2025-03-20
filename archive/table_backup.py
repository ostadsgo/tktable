import tkinter as tk
from tkinter import ttk


class Data:
    def __init__(self):
        self.g_dict = {
            "1234": {
                "t1": {"test1": {"time": [1, 2, 3], "amp": [9, 1, 8]}},
                "t2": {"test2": {"time": [0, 1, 0], "amp": [1, 4, 3]}},
            },
            "3421": {
                "t1": {"test1": {"time": [1, 2, 3], "amp": [9, 1, 8]}},
                "t2": {"test2": {"time": [0, 1, 0], "amp": [1, 4, 3]}},
                "t3": {"test3": {"time": [0, 1, 0], "amp": [1, 4, 3]}},
            },
        }

        self.test_dict = {"signal 1": {"time": [123], "amp": [123]}}

    def grids(self):
        return list(self.g_dict)

    def directions(self, grid):
        directions = []
        return self.g_dict[grid]


class TableFrame(ttk.Frame):
    def __init__(self, master, headers, **kwargs):
        super().__init__(master, **kwargs)

        self.headers = headers
        ### Variables
        self.rows = []
        self.row_frames = []
        self.cells = []
        self.check_all_var = tk.BooleanVar(value=False)
        self.check_row_vars = []
        self.widget_opts = dict(sticky="news")

        ### Styles
        # lightgray : d3d3d3
        self.style = ttk.Style()
        self.style.configure("DataFrame.TFrame", background="lightgray")
        self.style.configure("HeaderFrame.TFrame", background="#d3d3d3")
        self.style.configure("RowFrame.TFrame", background="#c8c8c8")
        self.style.configure("HighlightRowFrame.TFrame", background="#AC5858")
        self.style.configure("RowCheckbutton.TCheckbutton", background="#c8c8c8")

        ### Widgets
        # Frames
        # data_frame padding + row_frame padding = header_frame padding
        self.header_frame = ttk.Frame(self)
        self.data_frame = ttk.Frame(self)

        ### Grid widgets
        self.header_frame.grid(row=0, column=0, sticky="news")
        self.data_frame.grid(row=1, column=0, sticky="news")

        ### Table growth size
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)
        # Header Frame
        self.header_frame.rowconfigure(0, weight=1)
        # Header widgets growth size
        for i in range(1, len(self.headers) + 1):
            self.header_frame.columnconfigure(i, weight=1)
        # Data Frame
        self.data_frame.columnconfigure(0, weight=1)

        ### call methods
        self.create_header()

    def create_header(self):
        check_all_button = ttk.Checkbutton(
            self.header_frame,
            text="",
            variable=self.check_all_var,
            command=self.check_all_rows,
        )
        check_all_button.grid(row=0, column=0)

        for index, header in enumerate(self.headers, 1):
            ttk.Button(self.header_frame, text=header).grid(row=0, column=index)

    def on_select(self, event):
        print("selected")

    def create_row(self, widget_values=[], widget="Combobox"):
        # Row Frame widget
        row_frame = ttk.Frame(self.data_frame)
        row_frame.grid(row=len(self.row_frames), column=0)
        # store row_frame in row_frames list.
        self.row_frames.append(row_frame)

        # Checkbutton var
        check_var = tk.BooleanVar(value=False)
        self.check_row_vars.append(check_var)

        # Checkbutton widget
        check_row_button = ttk.Checkbutton(row_frame, text="", variable=check_var)
        check_row_button.grid(row=0, column=0)

        # Widget :: Comboboxes for a row
        for i, (widget, values) in enumerate(widget_values, 1):
            if widget == "Combobox":
                combo = ttk.Combobox(row_frame, values=values)
                combo.grid(row=0, column=i, **self.widget_opts)
                self.set_current(combo, values, 0)
                combo.bind("<<ComboboxSelected>>", self.on_select)
            elif widget == "Entry":
                entry = ttk.Entry(row_frame)
                entry.grid(row=0, column=i)
            else:
                raise ValueError(f"Widget {widget} not supported!")

        # Growth size same as header growth size
        # row_frame.rowconfigure(0, weight=1)
        for i in range(1, len(widget_values) + 1):
            row_frame.columnconfigure(i, weight=1)

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

    def set_current(self, combo, value, index=0):
        if value:
            combo.current(index)

    def remove_by_index(self, index):
        self.row_frames[index].destroy()
        del self.row_frames[index]
        del self.check_row_vars[index]


class ActionFrame(ttk.Frame):
    def __init__(self, master, table, **kwargs):
        super().__init__(master, **kwargs)
        self.table = table
        self.pack_opt = dict(fill=tk.X, expand=True, side=tk.LEFT)
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
        vals = []
        widgets_name = ["Combobox"] * 4 + ["Entry"] * 4
        values = [[]] * len(widgets_name)
        data = Data()
        grids = data.grids()
        values[0] = grids
        widget_values = list(zip(widgets_name, values))
        print(widget_values)

        self.table.create_row(widget_values)

    def remove_row(self):
        self.table.remove_row()

    def import_data(self):
        pass

    def export_data(self):
        pass


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        headers = ["hedaer " + str(i) for i in range(1, 9)]
        table = TableFrame(self, headers)
        table.grid(row=0, column=0, sticky="news")

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
        self.geometry("900x500")

        # Main frame
        mainframe = MainFrame(self)
        mainframe.grid(row=0, column=0, sticky="news")

        # Growth rate
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
