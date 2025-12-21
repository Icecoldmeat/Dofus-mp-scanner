import tkinter as tk


def show_overlay(x, y, width, height):
    # Create a new top-level window
    overlay = tk.Toplevel()
    overlay.overrideredirect(True)  # remove window decorations
    overlay.geometry(f"{width}x{height}+{x}+{y}")

    # Make window transparent
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.3)  # transparency (0.0 to 1.0)

    # Red background
    canvas = tk.Canvas(overlay, width=width, height=height, bg="red")
    canvas.pack()

    overlay.mainloop()


# Example: show a red transparent block at (100, 100) of size 200x150
show_overlay(720, 1024, 1920, 1080)