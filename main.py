import tkinter as tk
from tkinter import ttk

class Data:
    pass

class TableFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.header_frame = ttk.Frame(self, relief=tk.SOLID, padding=5)
        self.data_frame = ttk.Frame(self, relief=tk.SUNKEN, padding=5)
        self.headers = ["header 1", "header 2", "header 3", "header 4", "header 5"]
        self.rows = []
        self.row_frames = []

        self.ui()
        # Growth size
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=90)
        self.columnconfigure(0, weight=1)

    def ui(self):
        self.make_header()
        self.header_frame.grid(row=0, column=0, sticky="new")
        self.data_frame.grid(row=1, column=0, sticky="new")

    def make_header(self):
        for header in self.headers:
            ttk.Button(self.header_frame, text=header).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    def create_row(self, values=[]):
        row_frame  = ttk.Frame(self.data_frame)
        ttk.Combobox(row_frame, values=("Value 1", "Value 2", "Value 3")).pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        row_frame.pack(fill=tk.X, expand=True)
        self.row_frames.append(row_frame)


class ActionFrame(ttk.Frame):
    def __init__(self, master, table, **kwargs):
        super().__init__(master, **kwargs)
        self.table = table
        # Actions : buttons
        create_row_button = ttk.Button(self, text="+", command=self.create_row)
        remove_row_button = ttk.Button(self, text="-", command=self.remove_row)
        import_button = ttk.Button(self, text="Import", command=self.import_data)
        export_button = ttk.Button(self, text="Export", command=self.export_data)
        create_row_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))
        remove_row_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))
        import_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))
        export_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 5))

    def create_row(self):
        self.table.create_row(values=[1, 2, 3])

    def remove_row(self):
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
        self.geometry("800x650")
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
