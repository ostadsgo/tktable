
import tkinter as tk

def on_button_click(button_name):
    print(f"{button_name} clicked!")

# Create the main window
root = tk.Tk()
root.title("Table-like Layout")

# Create header
header = ["Header 1", "Header 2", "Header 3"]
for col, title in enumerate(header):
    label = tk.Label(root, text=title, font=("Arial", 14, "bold"))
    label.grid(row=0, column=col, padx=10, pady=5)

# Create buttons in the header
buttons = ["Button 1", "Button 2", "Button 3"]
for col, button_name in enumerate(buttons):
    button = tk.Button(root, text=button_name, command=lambda name=button_name: on_button_click(name))
    button.grid(row=1, column=col, padx=10, pady=5)

# Create rows of entries
for row in range(2, 5):  # Create 3 rows of entries
    for col in range(len(header)):
        entry = tk.Entry(root)
        entry.grid(row=row, column=col, padx=10, pady=5)

# Start the Tkinter event loop
root.mainloop()
