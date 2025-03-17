import tkinter as tk
from tkinter import ttk


class TableFrame(ttk.Frame):
    def __init__(self, master, headers, **kwargs):
        super().__init__(master, **kwargs)


        self.rows = []
        self.row_frames = []
        self.cells = []
        self.check_all_var = tk.BooleanVar(value=False)
        self.check_row_vars = []
        self.widget_opts = dict(sticky="news")


        self.headers = headers
        self.header_frame = ttk.Frame(self, relief="solid", padding=5)
        self.data_frame = ttk.Frame(self, relief="solid", padding=5)
        self.header_frame.grid(row=0, column=0, sticky="new")
        self.data_frame.grid(row=1, column=0, sticky="news")


        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)


        


        self.data_frame.columnconfigure(0, weight=1)



        self.create_header()

    def create_header(self):
        check_all_button = ttk.Checkbutton(
            self.header_frame,
            text="",
            variable=self.check_all_var,
        )
        check_all_button.grid(row=0, column=0, **self.widget_opts)

        for index, header in enumerate(self.headers, 1):
            ttk.Button(self.header_frame, text=header).grid(
                row=0, column=index, **self.widget_opts
            )
            self.header_frame.columnconfigure(index, weight=1)

    def create_row(self, widget_values=[], widget="Combobox"):
        # Row Frame widget
        row_frame = ttk.Frame(self.data_frame)
        row_frame.grid( row=len(self.row_frames), column=0, sticky="we")
        # store row_frame in row_frames list.
        self.row_frames.append(row_frame)

        # Checkbutton var
        check_var = tk.BooleanVar(value=False)
        self.check_row_vars.append(check_var)

        # Checkbutton widget
        check_row_button = ttk.Checkbutton(row_frame, text="", variable=check_var)
        check_row_button.grid(row=0, column=0, **self.widget_opts)

        # Widget :: Comboboxes for a row
        for i, (widget, values) in enumerate(widget_values, 1):
            if widget == "Combobox":
                combo = ttk.Combobox(row_frame, values=values)
                combo.grid(row=0, column=i, **self.widget_opts)
                combo.bind("<<ComboboxSelected>>", self.on_select)
            elif widget == "Entry":
                entry = ttk.Entry(row_frame)
                entry.grid(row=0, column=i, **self.widget_opts)
            else:
                raise ValueError(f"Widget {widget} not supported!")

            
            row_frame.columnconfigure(i, weight=1)
        



    def on_select(self, event=None):
        pass

class ActionFrame(ttk.Frame):
    def __init__(self, master, table, **kwargs):
        super().__init__(master, **kwargs)
        self.table = table
        self.pack_opt = dict(fill=tk.X, expand=True, side=tk.LEFT)
        # Actions : buttons
        create_row_button = ttk.Button(self, text="+", command=self.add_row)
        create_row_button.pack(**self.pack_opt)

    def add_row(self):
        vals = []
        widgets_name = ["Combobox"] * 4  + ["Entry"] * 4
        values = [[]] * len(widgets_name)
        # data = Data()
        # grids = data.grids()
        # values[0] = grids
        widget_values = list(zip(widgets_name, values))
        print(widget_values)

        self.table.create_row(widget_values)

class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        headers = ["hedaer " + str(i) for i in range(1, 9)]
        table = TableFrame(self, headers, relief="solid", padding=5)
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
