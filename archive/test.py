import tkinter as tk
import sys


def _on_mousewheel(event):
    if sys.platform == "win32":
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        else:
            canvas.yview_scroll(1, "units")
    else:
        if event.num == 5:
            canvas.yview_scroll(1, "units")
        if event.num == 4:
            canvas.yview_scroll(-1, "units")


root = tk.Tk()

# Create a canvas and add a scrollbar to it
canvas = tk.Canvas(root, width=400, height=200)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame within the canvas
frame = tk.Frame(canvas)

# Add the frame to the canvas
canvas.create_window((0, 0), window=frame, anchor="nw")

# Add some widgets to the frame
for i in range(50):
    label = tk.Label(frame, text=f"Label {i}")
    label.pack()

# Configure the scrollbar
canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the mouse wheel event to the scroll function
if sys.platform == "win32":
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
else:
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

# Pack the canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root.mainloop()
