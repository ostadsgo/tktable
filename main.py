import tkinter as tk
from tkinter import ttk

class Data:
    pass

class TableFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.header_frame = ttk.Frame(self, relief=tk.SOLID, padding=5)
        self.data_frame = ttk.Frame(self, relief=tk.SUNKEN, padding=5)
        # Variables
        self.headers = ["header 1", "header 2", "header 3", "header 4", "header 5"]
        self.rows = []
        self.row_frames = []
        self.check_all_var = tk.BooleanVar(value=False)
        self.pack_opt = dict(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        self.style = ttk.Style()

        self.ui()
        # Growth size
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)

    def ui(self):
        self.style.configure("Row.TFrame", background="#b6927b", padding=(5, 2))
        self.make_header()
        self.header_frame.grid(row=0, column=0, sticky="new")
        self.data_frame.grid(row=1, column=0, sticky="news")
        self.data_frame.columnconfigure(0, weight=1)

    def make_header(self):
        all_checkbutton = ttk.Checkbutton(self.header_frame, text="", variable=self.check_all_var)
        all_checkbutton.pack(side=tk.LEFT, fill=tk.X, expand=True)
        for header in self.headers:
            ttk.Button(self.header_frame, text=header).pack(**self.pack_opt)

    def create_row(self, values=[]):
        row_frame  = ttk.Frame(self.data_frame, background="red")
        self.var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row_frame, text="", variable=self.var, command=self.check_row).grid(row=0, column=0, sticky="e")
        ttk.Combobox(row_frame, values=("Value 1", "Value 2", "Value 3")).grid(row=0, column=1, sticky="new")
        ttk.Combobox(row_frame, values=("Value 1", "Value 2", "Value 3")).grid(row=0, column=2, sticky="new")
        ttk.Combobox(row_frame, values=("Value 1", "Value 2", "Value 3")).grid(row=0, column=3, sticky="new")
        ttk.Combobox(row_frame, values=("Value 1", "Value 2", "Value 3")).grid(row=0, column=4, sticky="new")
        ttk.Combobox(row_frame, values=("Value 1", "Value 2", "Value 3")).grid(row=0, column=5, sticky="new")
        row_frame.pack(fill=tk.X, expand=True)
        self.row_frames.append(row_frame)

    def check_row(self):
        print("hello")

    def get_data(self):
        pass


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
        self.table.create_row(values=[1, 2, 3])

    def remove_row(self):
        # Must check if multiple row_checkbutton checked must delete them
        # if no row_checkbutton checked delete last row
        pass

    def import_data(self):
        pass

    def export_data(self):
        pass


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        table = TableFrame(self, relief=tk.GROOVE, padding=10)
        table.grid(row=0, column=0, sticky="news")
        table.create_row()

        action = ActionFrame(self, table)
        action.grid(row=1, column=0, sticky="news")

        # Growth size : Responsive shit
        self.rowconfigure(0, weight=90)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=1)



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Table Like Widget")
        self.geometry("900x600")
        # Create mainframe 
        mainframe = MainFrame(self)
        mainframe.grid(row=0, column=0, sticky="wesn")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def run(self):
        self.mainloop()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
