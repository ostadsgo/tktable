from tkinter import ttk
import tkinter as tk

#NOTE: 
# mainframe sticky must be `news`
# 


def header(mainframe):
    hf = ttk.Frame(mainframe)
    hf.grid(row=0, column=0, sticky="we")
    for i in range(5):
        ttk.Button(hf, text="Header" + str(i)).grid(row=0, column=i, sticky="we", padx=5)
        hf.columnconfigure(i, weight=1)

def data(mainframe):
    df = ttk.Frame(mainframe)
    df.grid(row=1, column=0, sticky="news")
    df.columnconfigure(0, weight=1)
    for i in range(3):
        row_frame = ttk.Frame(df)
        for j in range(5):
            row_frame.grid(row=i, column=0, sticky="ew")
            ttk.Combobox(row_frame).grid(row=0, column=j, sticky="we", padx=5, pady=5)
            row_frame.columnconfigure(j, weight=1)




def mainframe(root):
    mf = ttk.Frame(root, padding=5, relief="sunken")
    mf.grid(row=0, column=0, padx=5, pady=5, sticky="news")

    mf.rowconfigure(0, weight=1)
    mf.rowconfigure(1, weight=99)
    mf.columnconfigure(0, weight=1)

    # Header
    header(mf)

    # Data
    data(mf)






def app():
    root = tk.Tk()
    root.geometry("700x400")

    # mainframe
    mainframe(root)


    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.mainloop()

app()
