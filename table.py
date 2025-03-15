# TODO: get_row to get data of a row: get_row(0)
# get_cell_data: to get data of a cell: get_cell_data(row=0, column=2)
# add_hi -> add hihglight for a row
# clear_hi -> clear highlight for a row
# NOTE: future ntoe

import tkinter as tk
from tkinter import ttk


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
        # make color dict

        ### Styles
        # lightgray : d3d3d3
        self.style = ttk.Style()
        self.style.configure("DataFrame.TFrame", background="lightgray")
        self.style.configure("HeaderFrame.TFrame", background="#d3d3d3")
        self.style.configure("RowFrame.TFrame", background="#c8c8c8")
        self.style.configure("HighlightRowFrame.TFrame", background="#AC5858")

        ### Widgets
        # Frames
        # data_frame padding + row_frame padding = header_frame padding
        self.header_frame = ttk.Frame(self, style="HeaderFrame.TFrame", padding=(10, 0)) 
        self.data_frame = ttk.Frame(self, style="DataFrame.TFrame", relief=tk.GROOVE, padding=5)

        ### Grid widgets
        self.header_frame.grid(row=0, column=0, sticky="news")
        self.data_frame.grid(row=1, column=0, sticky="news", pady=5)

        ### Table growth size
        self.rowconfigure(0, weight=1) 
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)
        # Header Frame
        self.header_frame.rowconfigure(0, weight=1)
        # Header widgets growth size
        print(len(self.headers))
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
        check_all_button.grid(sticky="we")

        for index, header in enumerate(self.headers, 1):
            ttk.Button(self.header_frame, text=header).grid(
                row=0, column=index, sticky="we", padx=1
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

    def create_row(self, widget_values=[], widget="Combobox"):
        # Row Frame widget
        row_frame = ttk.Frame(self.data_frame, style="RowFrame.TFrame", padding=(5, 8))
        row_frame.grid( row=len(self.row_frames), column=0, sticky="news", pady=3)
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
        for i, (widget, values) in enumerate(widget_values, 1):
            if widget == "Combobox":
                combo = ttk.Combobox(row_frame, values=values)
                combo.current(0)
                combo.grid(row=0, column=i, sticky="ew", padx=1)
            elif widget == "Entry":
                entry = ttk.Entry(row_frame)
                entry.grid(row=0, column=i, sticky="ew", padx=1)
            else:
                raise ValueError(f"Widget {widget} not supported!")

        # Growth size same as header growth size
        row_frame.rowconfigure(0, weight=1)
        # Make it dynamic as header_frame needed
        for i in range(1, len(widget_values)+1):
            row_frame.columnconfigure(i, weight=10)

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
        vals = [
            [random.randrange(100) for i in range(random.randrange(1, 10))]
            for i in range(4)
        ] + [[]] * 4

        widgets_name = ["Combobox"] * 4  + ["Entry"] * 4

        widget_values = list(zip(widgets_name, vals))

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
        mainframe = MainFrame(self, padding=5)
        mainframe.grid(row=0, column=0, sticky="news")

        # Growth rate
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
