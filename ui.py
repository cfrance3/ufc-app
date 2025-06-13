from tkinter import *
from PIL import Image, ImageTk, ImageSequence

BACKGROUND_COLOR = "#262626"
LIGHT_BACKGROUND_COLOR = "#3A3A3A"
UFC_RED = "#CC0000"
ACCENT_COLOR = "#900000"
HIGHLIGHT_COLOR = "#BB3627"

def clear_screen(container):
    for widget in container.winfo_children():
        widget.destroy()

def set_row_column_weights(container, rows=None, row_weight=1, columns=None, column_weight=1):
    if rows:
        for r in rows:
            container.grid_rowconfigure(r, weight=row_weight)
    if columns:
        for c in columns:
            container.grid_columnconfigure(c, weight=column_weight)

def create_canvas_button(container, text, row, column, command, width, height, bg_color=UFC_RED, hover_color=HIGHLIGHT_COLOR, text_color='white', font=("Open Sans", 18)):
    canvas = Canvas(container, width=width, height=height, highlightthickness=0, bg=BACKGROUND_COLOR)
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

def refresh_random_fight(container, app_state):
    app_state.get_random_fight(app_state.db_manager)

    for widget in container.winfo_children():
        widget.destroy()

    create_random_fight_widgets(container, app_state)



def create_random_fight_widgets(container, app_state):
    if not app_state.current_fight:
        app_state.get_random_fight(app_state.db_manager)
    fight = app_state.current_fight
    fight_border_frame = Frame(container, highlightbackground=UFC_RED, highlightthickness=3)
    fight_border_frame.grid(row=0, column=0, pady=(0,10))
    fight_frame = Frame(fight_border_frame, bg=LIGHT_BACKGROUND_COLOR)
    fight_frame.grid(row=0, column=0)
    fight_frame.grid_columnconfigure(0, weight=1)
    fight_frame.grid_columnconfigure(1, weight=0)
    fight_frame.grid_columnconfigure(2, weight=1)

    if fight:
        title_label = Label(fight_frame, text="Random Fight Spotlight", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 24))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        weight_class_text = fight['weight_class'] + " Title Bout" if fight['title_fight'] else fight['weight_class'] + " Bout"
        bout_info_text = f"Event: {fight['event_name']}\nDate: {fight['date']}\n{weight_class_text}"
        bout_info_label = Label(fight_frame, text=bout_info_text, bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 16))
        bout_info_label.grid(row=1, column=0, columnspan=3, pady=(0,10))

        test_font = ("Open Sans", 20)
        hidden_label1 = Label(container, text=fight['fighter1_name'], font=test_font)
        hidden_label1.update_idletasks()
        name1_width = hidden_label1.winfo_reqwidth()
        hidden_label1.destroy()

        hidden_label2 = Label(container, text=fight['fighter2_name'], font=test_font)
        hidden_label2.update_idletasks()
        name2_width = hidden_label2.winfo_reqwidth()
        hidden_label2.destroy()

        max_name_width_px = max(name1_width, name2_width)
        max_name_width_char = int(max_name_width_px / 12)

        fighter1_frame = Frame(fight_frame, bg=LIGHT_BACKGROUND_COLOR)
        fighter1_frame.grid(row=2, column=0, sticky='e')
        fighter1_frame.grid_columnconfigure(0, weight=1)
        fighter1_name_label = Label(fighter1_frame, text=f"{fight['fighter1_name']}", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 20), width=max_name_width_char)
        fighter1_name_label.grid(row=0, column=0, sticky='n')
        fighter1_attr_text = f"{fight['fighter1_height']}\n{fight['fighter1_reach']}\n{fight['fighter1_stance']}\n{fight['fighter1_sig_strikes']} / {fight['fighter1_sig_strikes_att']}\n{fight['fighter1_total_strikes']} / {fight['fighter1_total_strikes_att']}\n{fight['fighter1_head_strikes']} / {fight['fighter1_head_strikes_att']}\n{fight['fighter1_body_strikes']} / {fight['fighter1_body_strikes_att']}\n{fight['fighter1_leg_strikes']} / {fight['fighter1_leg_strikes_att']}\n{fight['fighter1_takedowns']} / {fight['fighter1_takedowns_att']}"
        fighter1_attr_label = Label(fighter1_frame, text=fighter1_attr_text, bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 14), justify='center')
        fighter1_attr_label.grid(row=1, column=0)

        fighter_attr_frame = Frame(fight_frame, bg=LIGHT_BACKGROUND_COLOR)
        fighter_attr_frame.grid(row=2, column=1)
        fighter_attr_frame.grid_columnconfigure(0, weight=1)
        blank_label = Label(fighter_attr_frame, text="   ", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 20))
        blank_label.grid(row=0, column=0, sticky='ew')
        attr_label = Label(fighter_attr_frame, text="Height\nReach\nStance\nSig. Strikes\nTot. Strikes\nHead\nBody\nLeg\nTD", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 14))
        attr_label.grid(row=1, column=0, sticky='ew')

        fighter2_frame = Frame(fight_frame, bg=LIGHT_BACKGROUND_COLOR)
        fighter2_frame.grid(row=2, column=2, sticky='w')
        fighter2_frame.grid_columnconfigure(0, weight=1)
        fighter2_name_label = Label(fighter2_frame, text=f"{fight['fighter2_name']}", bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 20), width=max_name_width_char)
        fighter2_name_label.grid(row=0, column=0, sticky='n')
        fighter2_attr_text = f"{fight['fighter2_height']}\n{fight['fighter2_reach']}\n{fight['fighter2_stance']}\n{fight['fighter2_sig_strikes']} / {fight['fighter2_sig_strikes_att']}\n{fight['fighter2_total_strikes']} / {fight['fighter2_total_strikes_att']}\n{fight['fighter2_head_strikes']} / {fight['fighter2_head_strikes_att']}\n{fight['fighter2_body_strikes']} / {fight['fighter2_body_strikes_att']}\n{fight['fighter2_leg_strikes']} / {fight['fighter2_leg_strikes_att']}\n{fight['fighter2_takedowns']} / {fight['fighter2_takedowns_att']}"
        fighter2_attr_label = Label(fighter2_frame, text=fighter2_attr_text, bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 14), justify='center')
        fighter2_attr_label.grid(row=1, column=0)

        outcome_text = f"Winner: {fight['winner']}\nMethod: {fight['method']}"
        outcome_label = Label(fight_frame, text=outcome_text, bg=LIGHT_BACKGROUND_COLOR, fg='white', font=("Open Sans", 16))
        outcome_label.grid(row=3, column=0, columnspan=3, pady=(10,0))

        create_canvas_button(container, "NEW FIGHT", 1, 0, lambda: refresh_random_fight(container, app_state), 120, 60)

    else:
        label = Label(fight_frame, text="An error has occured. Please restart the app.", bg=BACKGROUND_COLOR, fg='white', font=("Open Sans", 14))
        label.grid(row=0, column=0, columnspan=3)

def show_random_fight_spotlight(container, app_state):
    spotlight_frame = Frame(container, bg=BACKGROUND_COLOR)
    spotlight_frame.grid(row=2, column=0, pady=(20,0))

    create_random_fight_widgets(spotlight_frame, app_state)


def show_menu_buttons(container, app_state):
    button_frame = Frame(container, bg=BACKGROUND_COLOR)
    button_frame.grid(row=1, column=0, columnspan=6)
    create_canvas_button(button_frame, "HOME", 1, 0, lambda: main_page(container, app_state), 120, 60)
    create_canvas_button(button_frame, "EVENTS", 1, 1, lambda: events_page(container, app_state), 120, 60)
    create_canvas_button(button_frame, "WEIGHTS", 1, 2, lambda: weights_page(container, app_state), 120, 60)
    create_canvas_button(button_frame, "FIGHTS", 1, 3, lambda: fights_page(container, app_state), 120, 60)
    create_canvas_button(button_frame, "FIGHTERS", 1, 4, lambda: fighters_page(container, app_state), 120, 60)
    create_canvas_button(button_frame, "SEARCH", 1, 5, lambda: search_page(container, app_state), 120, 60)
    

def fighter_ui(root):
    clear_screen(root)
    label = Label(root, bg='green')
    label.pack()

def main_page(root, app_state):
    if app_state.current_page == "home":
        return
    app_state.current_page = "home"
    clear_screen(root)

    container = Frame(root, bg=BACKGROUND_COLOR)
    container.grid(row=0, column=0, sticky="nsew")
    set_row_column_weights(container, columns=[0])


    title_label = Label(container, text="UFC Database", bg=BACKGROUND_COLOR, font=("Open Sans", 36))
    title_label.grid(row=0, column=0, pady=10)

    show_menu_buttons(container, app_state)

    show_random_fight_spotlight(container, app_state)

    # container.update_idletasks()

def events_page(root, app_state):
    if app_state.current_page == "events":
        return
    app_state.current_page = "events"
    clear_screen(root)

    container = Frame(root, bg=BACKGROUND_COLOR)
    container.grid(row=0, column=0, sticky="nsew")
    set_row_column_weights(container, columns=[0])

    title_label = Label(container, text="Events", bg=BACKGROUND_COLOR, font=("Open Sans", 36))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    show_menu_buttons(container, app_state)

def weights_page(root, app_state):
    if app_state.current_page == "weights":
        return
    app_state.current_page = "weights"
    clear_screen(root)

    container = Frame(root, bg=BACKGROUND_COLOR)
    container.grid(row=0, column=0, sticky="nsew")
    set_row_column_weights(container, columns=[0])

    title_label = Label(container, text="Weight Classes", bg=BACKGROUND_COLOR, font=("Open Sans", 36))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    show_menu_buttons(container, app_state)

def fights_page(root, app_state):
    if app_state.current_page == "fights":
        return
    app_state.current_page = "fights"
    clear_screen(root)

    container = Frame(root, bg=BACKGROUND_COLOR)
    container.grid(row=0, column=0, sticky="nsew")
    set_row_column_weights(container, columns=[0])

    title_label = Label(container, text="Fights", bg=BACKGROUND_COLOR, font=("Open Sans", 36))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    show_menu_buttons(container, app_state)

def fighters_page(root, app_state):
    if app_state.current_page == "fighters":
        return
    app_state.current_page = "fighters"
    clear_screen(root)

    container = Frame(root, bg=BACKGROUND_COLOR)
    container.grid(row=0, column=0, sticky="nsew")
    set_row_column_weights(container, columns=[0])

    title_label = Label(container, text="Fighters", bg=BACKGROUND_COLOR, font=("Open Sans", 36))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    show_menu_buttons(container, app_state)

def search_page(root, app_state):
    if app_state.current_page == "search":
        return
    app_state.current_page = "search"
    clear_screen(root)

    container = Frame(root, bg=BACKGROUND_COLOR)
    container.grid(row=0, column=0, sticky="nsew")
    set_row_column_weights(container, columns=[0])

    title_label = Label(container, text="Search", bg=BACKGROUND_COLOR, font=("Open Sans", 36))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    show_menu_buttons(container, app_state)
    

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