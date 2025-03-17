import tkinter as tk
from tkinter import ttk



class TableFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        self.headers = kwargs.pop("headers", [])
        self.widgets = kwargs.pop("widgets", ["Entry"])
        super().__init__(master, **kwargs)

        ### Vars
        self.rows = []
        self.row_frames = []
        self.check_row_vars = []
        self.check_all_var = tk.BooleanVar(value=False)

        ### self config
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)

        ### header 
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="we") 
        self.header_frame.rowconfigure(0, weight=1)
        self.create_header()

        ### Data frame
        self.data_frame = ttk.Frame(self)
        self.data_frame.grid(row=1, column=0, sticky="news")
        self.data_frame.columnconfigure(0, weight=1)

        for i in range(1, len(self.headers)+1):
            self.columnconfigure(i, weight=1) 

    def on_check_all(self):
        state = self.check_all_var.get()
        for var in self.check_row_vars:
            var.set(state)

    def create_header(self):
        # Checkbutton 
        check_all_button = ttk.Checkbutton(self.header_frame, variable=self.check_all_var, command=self.on_check_all)
        check_all_button.grid(row=0, column=0, sticky="we")

        # Header buttons
        for i, header in enumerate(self.headers, 1):
            ttk.Button(self.header_frame, text=header).grid(row=0, column=i, sticky="we")
            self.header_frame.columnconfigure(i, weight=1, uniform="a")

    def create_row(self, values=[]):
        # Row frame
        row_frame = ttk.Frame(self.data_frame)
        row_frame.grid(row=len(self.row_frames), column=0, sticky="we", columnspan=len(self.headers)+1)
        self.row_frames.append(row_frame)

        # Checkbutton for a row
        check_row_var = tk.BooleanVar(value=False)
        self.check_row_vars.append(check_row_var)
        check_row_button = ttk.Checkbutton(row_frame, variable=check_row_var)
        check_row_button.grid(row=0, column=0)

        # Widgets for a row
        for i, widget in enumerate(self.widgets, 1):
            if widget == "Combobox":
                ttk.Combobox(row_frame, values=(1,2, 3)).grid(row=0, column=i, sticky="news")
            elif widget == "Entry":
                ttk.Entry(row_frame).grid(row=0, column=i, sticky="news")
            else:
                raise ValueError("Error: Cannot create row. Unknown widget!!!")
            row_frame.columnconfigure(i, weight=1, uniform="a")


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

    def remove_by_index(self, index):
        self.row_frames[index].destroy()
        del self.row_frames[index]
        del self.check_row_vars[index]


class ActionFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        self.table = kwargs.pop("table")
        super().__init__(master, **kwargs)

        # self config
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # widgets
        pack_opts = dict(fill=tk.X, expand=True, side=tk.LEFT)
        ttk.Button(self, text="+", command=self.add_row).pack(**pack_opts)
        ttk.Button(self, text="-", command=self.remove_row).pack(**pack_opts)
        ttk.Button(self, text="Import", command=self.import_data).pack(**pack_opts)
        ttk.Button(self, text="Export", command=self.export_data).pack(**pack_opts)


    def add_row(self):
        values = []
        self.table.create_row(values=[])

    def remove_row(self):
        self.table.remove_row()
    def import_data(self):
        pass
    def export_data(self):
        pass


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        headers = [f"header {i+1}" for i in range(8)]
        ### Table
        widgets = [*["Combobox"] * 4, *["Entry"] * 4]
        # widgets = [*["Combobox"] * 4]
        print(widgets)
        table = TableFrame(self, headers=headers, widgets=widgets)
        table.grid(row=0, column=0, sticky="news")

        ### Actions
        ActionFrame(self, table=table).grid(row=1, column=0, sticky="nwes")



class App(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__()
        self.title("Table Example")
        self.geometry("700x400")
        self._ui()
        self._config()

    def _ui(self):
        mainframe = MainFrame(self, padding=5)
        mainframe.grid(row=0, column=0, sticky="news")
        mainframe.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)

    def _config(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def run(self):
        self.mainloop()


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()



