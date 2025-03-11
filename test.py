import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Resizable Frames Example")
root.geometry("300x200")

# Create a frame for buttons
button_frame = ttk.Frame(root)
button_frame.grid(row=0, sticky="ew")  # Expand in the east-west direction

# Create buttons
button1 = ttk.Button(button_frame, text="Button 1")
button1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

button2 = ttk.Button(button_frame, text="Button 2")
button2.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

# Create a frame for entries
entry_frame = ttk.Frame(root)
entry_frame.grid(row=1, sticky="ew")  # Expand in the east-west direction

# Create entry fields
entry1 = ttk.Entry(entry_frame)
entry1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

entry2 = ttk.Entry(entry_frame)
entry2.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

# Configure grid weights to allow resizing
root.grid_rowconfigure(0, weight=1)  # Allow the button frame to expand
root.grid_rowconfigure(1, weight=1)  # Allow the entry frame to expand
button_frame.grid_columnconfigure(0, weight=1)  # Allow button columns to expand
button_frame.grid_columnconfigure(1, weight=1)  # Allow button columns to expand
entry_frame.grid_columnconfigure(0, weight=1)  # Allow entry columns to expand
entry_frame.grid_columnconfigure(1, weight=1)  # Allow entry columns to expand


# Start the Tkinter event loop
root.mainloop()
