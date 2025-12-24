import tkinter as tk
from tkinter import messagebox

class OverlayBox:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window title bar
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)  # Transparency
        self.root.configure(bg="red")

        # Initial size and position
        self.root.geometry("200x150+100+100")

        # Variables for dragging
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Variables for resizing
        self.resizing = False
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0

        # Bind mouse events
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Button-3>", self.start_resize)
        self.root.bind("<B3-Motion>", self.do_resize)

        # Bind F2 to finish
        self.root.bind("<F2>", self.finish)

        self.region = None

    def start_move(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.resizing = True
        self.resize_start_x = event.x
        self.resize_start_y = event.y
        self.resize_start_width = self.root.winfo_width()
        self.resize_start_height = self.root.winfo_height()

    def do_resize(self, event):
        if self.resizing:
            width = max(20, self.resize_start_width + (event.x - self.resize_start_x))
            height = max(20, self.resize_start_height + (event.y - self.resize_start_y))
            self.root.geometry(f"{width}x{height}")

    def finish(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        self.region = (x, y, width, height)
        self.root.destroy()

    def run(self):
        messagebox.showinfo("Instructions", "Left-click drag: move box\nRight-click drag: resize box\nPress F2: finish and get coordinates")
        self.root.mainloop()
        return self.region

if __name__ == "__main__":
    box = OverlayBox()
    region = box.run()
    print("Selected region:", region)


#Left mouse button drag → move the box.
#Right mouse button drag → resize the box.
#F2 → prints the final (x, y, width, height) and closes the overlay.
#Transparent red overlay (alpha=0.3) stays on top.


#Selected region: (845, 287, 464, 71) -> item box