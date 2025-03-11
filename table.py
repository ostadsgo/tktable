import tkinter as tk
from tkinter import ttk


class TableFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ### Variables
        self.rows = []
        self.row_frames = []
        self.cells = []

        ### Styles
        self.style = ttk.Style()
        self.style.configure("DataFrame.TFrame", background="#708090")
        self.style.configure("RowFrame.TFrame", background="#789978")
        self.style.configure("HeaderFrame.TFrame", background="#b6927b")

        ### Widgets
        # Frames
        self.header_frame = ttk.Frame(self, style="HeaderFrame.TFrame", padding=10)
        self.data_frame = ttk.Frame(self, style="DataFrame.TFrame")

        ### Grid widgets
        self.header_frame.grid(row=0, column=0, sticky="nwe")
        self.data_frame.grid(row=1, column=0, sticky="news")

        ### Growth size
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=99)
        self.columnconfigure(0, weight=1)
        # Header Frame
        self.header_frame.rowconfigure(0, weight=1)

        # Data Frame
        self.data_frame.columnconfigure(0, weight=1)


    def create_header(self, headers=[]):
        for index, header in enumerate(headers):
            ttk.Button(self.header_frame, text=header).grid(row=0, column=index, sticky="we")

    def create_row(self, row_frame, row=[], widget="Combobox"):
        if widget not in ["Checkbutton", "Combobox", "Entry"]:
            return "Error: Widget not supported."

        for index, values in enumerate(row):
            if widget == "Checkbutton":
                pass
            if widget == "Combobox":
                ttk.Combobox(row_frame, values=values).grid(row=0, column=index)
            if widget == "Entry":
                pass

            row_frame.grid(row=index, column=0, sticky="news", padx=5, pady=5)



    def create_rows(self, rows=[]):
        for index, row in enumerate(rows):
            row_frame = ttk.Frame(self.data_frame, padding=10, style="RowFrame.TFrame")
            self.create_row(row_frame, row)
            self.row_frames.append(row_frame)



class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        table = TableFrame(self, padding=10)
        table.grid(row=0, column=0, sticky="news")
        headers = ["hedaer " + str(i) for i in range(1, 6)]
        rows = []
        row1 = [["Yes", "No", "Yep"], ['a', 'b'], ["Hello"], ["good", "bye"]]
        row2 = [[1, 2, 3], [0, 1], [9]]
        rows.append(row1)
        rows.append(row2)
        
        table.create_header(headers)
        table.create_rows(rows)

        # Growth rate
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Root window options
        self.title("Table Like Widget")
        self.geometry("900x600")

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
