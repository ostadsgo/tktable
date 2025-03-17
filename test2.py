from tkinter import ttk
import tkinter as tk

row = 1
def create_row(table):
    global row
    ttk.Combobox(table).grid(row=row, column=0, sticky="we")
    ttk.Combobox(table).grid(row=row, column=1, sticky="we")
    ttk.Entry(table).grid(row=row, column=2, sticky="we")
    ttk.Entry(table).grid(row=row, column=3, sticky="we")
    row += 1

def create_header(table):
    for i in range(4):
        ttk.Button(table, text=f"Header {i+1}").grid(row=0, column=i, sticky="we")
        table.columnconfigure(i, weight=1)


def main():
    root = tk.Tk()
    root.geometry("400x300")

    table = ttk.Frame(root)
    table.grid(row=0, column=0, sticky="news")

    action = ttk.Frame(root)
    action.grid(row=1, column=0, sticky="s")

    create_header(table)
    
    table.columnconfigure(0, weight=1)
    ttk.Button(action, text="Add row", command=lambda: create_row(table)).grid(row=0, column=0)


    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.mainloop()

main()
