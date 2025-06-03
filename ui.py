from tkinter import *
from PIL import Image, ImageTk, ImageSequence

BACKGROUND_COLOR = "#262626"
UFC_RED = "#CC0000"
ACCENT_COLOR = "#900000"
HIGHLIGHT_COLOR = "#BB3627"

def clear_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

def set_row_column_weights(root, rows=None, row_weight=1, columns=None, column_weight=1):
    if rows:
        for r in rows:
            root.grid_rowconfigure(r, weight=row_weight)
    if columns:
        for c in columns:
            root.grid_columnconfigure(c, weight=column_weight)

def create_canvas_button(root, text, row, column, command, width, height, bg_color=UFC_RED, hover_color=HIGHLIGHT_COLOR, text_color='white', font=("Open Sans", 18)):
    canvas = Canvas(root, width=width, height=height, highlightthickness=0, bg=BACKGROUND_COLOR)
    canvas.grid(row=row, column=column)

    rect = canvas.create_rectangle(1, 1, width-1, height-1, fill=bg_color, outline=ACCENT_COLOR)
    label = canvas.create_text(width // 2, height // 2, text=text, fill=text_color, font=font)

    def on_enter(event):
        canvas.itemconfig(rect, fill=hover_color)

    def on_leave(event):
        canvas.itemconfig(rect, fill=bg_color)

    def on_click(event):
        command()

    for tag in (rect, label):
        canvas.tag_bind(tag, '<Enter>', on_enter)
        canvas.tag_bind(tag, '<Leave>', on_leave)
        canvas.tag_bind(tag, '<Button-1>', on_click)

    return canvas

def fighter_ui(root):
    clear_screen(root)
    label = Label(root, bg='green')
    label.pack()

def main_ui(root):
    clear_screen(root)

    Label(root, text="UFC Database", bg=BACKGROUND_COLOR, font=("Open Sans", 36)).grid(row=0, column=0, columnspan=4, pady=10)

    button_frame = Frame(root, bg=BACKGROUND_COLOR)
    button_frame.grid(row=1, column=0, columnspan=5)
    create_canvas_button(button_frame, "EVENTS", 1, 0, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "WEIGHTS", 1, 1, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "FIGHTS", 1, 2, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "FIGHTERS", 1, 3, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "SEARCH", 1, 4, lambda: fighter_ui(root), 120, 60)

    

    

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
        self.label = Label(parent, bg=BACKGROUND_COLOR)
        self.label.grid(row=0)

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