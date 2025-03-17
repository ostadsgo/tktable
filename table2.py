import tkinter as tk
from tkinter import ttk



class TableFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        self.headers = kwargs.pop("headers", [])
        self.widgets = kwargs.pop("widgets", ["Entry"])
        super().__init__(master, **kwargs)

        ### Vars
        self.row_num = 0
        self.rows = []
        self.rows_widget = []
        self.row_frames = []
        self.check_row_vars = []
        self.check_all_var = tk.BooleanVar(value=False)

        ### self
        
        self.columnconfigure([*range(1, len(self.headers)+1)], weight=1)
        self.create_header()

    def on_check_all(self):
        state = self.check_all_var.get()
        for var in self.check_row_vars:
            var.set(state)

    def create_header(self):
        # Checkbutton 
        check_all_button = ttk.Checkbutton(self, variable=self.check_all_var, command=self.on_check_all)
        check_all_button.grid(row=self.row_num, column=0, sticky="we")

        # Header buttons
        for i, header in enumerate(self.headers, 1):
            ttk.Button(self, text=header).grid(row=self.row_num, column=i, sticky="we")
            # self.columnconfigure(i, weight=1, uniform="a")
        self.row_num += 1

    def create_row(self, values=[]):
        # Row frame
        # Checkbutton for a row
        check_row_var = tk.BooleanVar(value=False)
        self.check_row_vars.append(check_row_var)
        check_row_button = ttk.Checkbutton(self, variable=check_row_var)
        check_row_button.grid(row=self.row_num, column=0)

        row_widgets = []
        # Widgets for a row
        for i, widget in enumerate(self.widgets, 1):
            if widget == "Combobox":
                w = ttk.Combobox(self, values=(1,2, 3))
            elif widget == "Entry":
                w = ttk.Entry(self)
            else:
                raise ValueError("Error: Cannot create row. Unknown widget!!!")
            w.grid(row=self.row_num, column=i, sticky="news")
            row_widgets.append(w)
        self.rows_widget.append(row_widgets)
        self.row_num += 1

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



