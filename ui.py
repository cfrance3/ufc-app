from tkinter import *
from PIL import Image, ImageTk, ImageSequence

BACKGROUND_COLOR = "#262626"
LIGHT_BACKGROUND_COLOR = "#3A3A3A"
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

def show_random_fight(root, db_manager):
    fight = db_manager.get_random_fight()
    fight_border_frame = Frame(root, highlightbackground=UFC_RED, highlightthickness=3)
    fight_border_frame.grid(row=2, column=0, pady=30)
    fight_frame = Frame(fight_border_frame, bg=LIGHT_BACKGROUND_COLOR)
    fight_frame.grid(row=0, column=0)
    fight_frame.grid_columnconfigure(0, weight=1)
    fight_frame.grid_columnconfigure(1, weight=0)
    fight_frame.grid_columnconfigure(2, weight=1)

    if fight:
        title_label = Label(fight_frame, text="Random Fight Spotlight", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 24))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        fighter1_frame = Frame(fight_frame, bg=LIGHT_BACKGROUND_COLOR)
        fighter1_frame.grid(row=1, column=0, sticky='e')
        fighter1_frame.grid_columnconfigure(0, weight=1)
        fighter1_name_label = Label(fighter1_frame, text=f"{fight['fighter1_name']}", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 20))
        fighter1_name_label.grid(row=0, column=0, sticky='n')
        fighter1_attr_text = f"{fight['fighter1_height']}\n{fight['fighter1_weight']}\n{fight['fighter1_stance']}"
        fighter1_attr_label = Label(fighter1_frame, text=fighter1_attr_text, bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 14), justify='center')
        fighter1_attr_label.grid(row=1, column=0)

        fighter_attr_frame = Frame(fight_frame, bg=LIGHT_BACKGROUND_COLOR, padx=25)
        fighter_attr_frame.grid(row=1, column=1)
        fighter_attr_frame.grid_columnconfigure(0, weight=1)
        blank_label = Label(fighter_attr_frame, text="   ", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 20))
        blank_label.grid(row=0, column=0, sticky='ew')
        attr_label = Label(fighter_attr_frame, text="Height\nWeight\nStance", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 14))
        attr_label.grid(row=1, column=0, sticky='ew')

        fighter2_frame = Frame(fight_frame, bg=LIGHT_BACKGROUND_COLOR)
        fighter2_frame.grid(row=1, column=2, sticky='w')
        fighter2_frame.grid_columnconfigure(0, weight=1)
        fighter2_name_label = Label(fighter2_frame, text=f"{fight['fighter2_name']}", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 20))
        fighter2_name_label.grid(row=0, column=0, sticky='n')
        fighter2_attr_text = f"{fight['fighter2_height']}\n{fight['fighter2_weight']}\n{fight['fighter2_stance']}"
        fighter2_attr_label = Label(fighter2_frame, text=fighter2_attr_text, bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 14), justify='center')
        fighter2_attr_label.grid(row=1, column=0)

        fight_frame.update_idletasks()
        fighter1_width = fighter1_frame.winfo_width()
        fighter2_width = fighter2_frame.winfo_width()
        max_width = max(fighter1_width, fighter2_width)
        fighter1_frame.config(width=max_width)
        fighter2_frame.config(width=max_width)
        fight_frame.grid_columnconfigure(0, minsize=max_width)
        fight_frame.grid_columnconfigure(2, minsize=max_width)

        fighter1_gap = fighter1_attr_label.winfo_x()
        fighter2_gap = fighter2_attr_label.winfo_x()
        padding_needed = max(fighter1_gap, fighter2_gap) - min(fighter1_gap, fighter2_gap)
        if fighter1_gap > fighter2_gap:
            fighter2_frame.grid(row=1, column=2, sticky='w', padx=(padding_needed, 0))
        else:
            fighter1_frame.grid(row=1, column=0, sticky='e', padx=(0, padding_needed))

    else:
        label = Label(fight_frame, text="No fights found", bg=BACKGROUND_COLOR, fg='white', font=("Open Sans", 14))
        label.grid(row=0, column=0, columnspan=3)



def fighter_ui(root):
    clear_screen(root)
    label = Label(root, bg='green')
    label.pack()

def main_ui(root, db_manager):
    clear_screen(root)

    Label(root, text="UFC Database", bg=BACKGROUND_COLOR, font=("Open Sans", 36)).grid(row=0, column=0, columnspan=4, pady=10)

    button_frame = Frame(root, bg=BACKGROUND_COLOR)
    button_frame.grid(row=1, column=0, columnspan=5)
    create_canvas_button(button_frame, "EVENTS", 1, 0, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "WEIGHTS", 1, 1, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "FIGHTS", 1, 2, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "FIGHTERS", 1, 3, lambda: fighter_ui(root), 120, 60)
    create_canvas_button(button_frame, "SEARCH", 1, 4, lambda: fighter_ui(root), 120, 60)

    show_random_fight(root, db_manager)


    

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