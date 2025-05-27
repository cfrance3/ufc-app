import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

BACKGROUND_COLOR = "#555454"

def main_ui(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("UFC Database")
    label = tk.Label(root, bg=BACKGROUND_COLOR, text="Welcome to the UFC Database!", font=("Helvetica", 16))
    label.pack(pady=20)

class GIFSpinner:
    def animate(self):
            if not hasattr(self, "frames") or not self.frames or not self.running:
                return
            
            frame = self.frames[self.frame_index]
            if not self.label.winfo_exists():
                return
            self.label.configure(image=frame)
            self.label.image = frame
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.parent.after(17, self.animate)

    def stop(self):
        self.running = False

    def __init__(self, parent, gif_path, scale=0.5):
        self.parent = parent
        self.running = True
        self.label = tk.Label(parent, bg=BACKGROUND_COLOR)
        self.label.pack(pady=40)

        try:
            self.gif = Image.open(gif_path)
        except Exception as e:
            print(f"Failed to load GIF: {e}")
            self.frames = []
            return
        self.frames = [
            ImageTk.PhotoImage(
                frame.copy().convert("RGBA").resize(
                    (int(frame.width * scale), int(frame.height * scale)),
                    Image.Resampling.LANCZOS
                )
            )
            for frame in ImageSequence.Iterator(self.gif)
        ]
        
        self.frame_index = 0
        self.animate()