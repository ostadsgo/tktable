
from tkinter import ttk
import tkinter as tk

row_num = 0

def header(mainframe):
    hf = ttk.Frame(mainframe)
    hf.grid(row=0, column=0, sticky="we")
    checkbutton = ttk.Checkbutton(hf)
    checkbutton.grid(row=0, column=0)
    for i in range(1, 9):
        ttk.Button(hf, text="Header" + str(i)).grid(row=0, column=i, sticky="we")
        hf.columnconfigure(i, weight=1)

def data(mainframe):
    df = ttk.Frame(mainframe)
    df.grid(row=1, column=0, sticky="news")
    df.columnconfigure(0, weight=1)
    for i in range(1, 9):
        df.columnconfigure(i, weight=1, uniform="a")  # Configure columns for the data frame
    return df

def create_row(df):
    global row_num
    row_frame = ttk.Frame(df)
    row_frame.grid(row=row_num, column=0, sticky="we")
    row_num += 1  # Corrected to increment the row_num
    checkbutton = ttk.Checkbutton(row_frame)
    checkbutton.grid(row=0, column=0)
    for i in range(1, 9):
        if i > 5:
            ttk.Entry(row_frame).grid(row=0, column=i, sticky="we")
        else:
            ttk.Combobox(row_frame).grid(row=0, column=i, sticky="we")

        row_frame.columnconfigure(i, weight=1, uniform="a")  # Configure columns for the row frame

def mainframe(root):
    mf = ttk.Frame(root, padding=5, relief="sunken")
    mf.grid(row=0, column=0, padx=5, pady=5, sticky="news")

    mf.rowconfigure(0, weight=1)
    mf.rowconfigure(1, weight=99)
    mf.columnconfigure(0, weight=1)

    # Header
    header(mf)

    # Data
    df = data(mf)

    ttk.Button(mf, text="Click", command=lambda: create_row(df)).grid(row=2, column=0)

def app():
    root = tk.Tk()
    root.geometry("700x400")

    # mainframe
    mainframe(root)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.mainloop()

app()
