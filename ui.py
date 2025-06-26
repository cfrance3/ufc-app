from tkinter import *
from tkinter import ttk
import math
from PIL import Image, ImageTk, ImageSequence

BACKGROUND_COLOR = "#262626"
LIGHT_BACKGROUND_COLOR = "#3A3A3A"
UFC_RED = "#CC0000"
ACCENT_COLOR = "#900000"
HIGHLIGHT_COLOR = "#BB3627"
LIST_ENTRIES_PER_PAGE = 50


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

def create_canvas_button(container, text, row, column, command, width, height, bg_color=UFC_RED, hover_color=HIGHLIGHT_COLOR, text_color='white', font=("Open Sans", 18), padx=0):
    canvas = Canvas(container, width=width, height=height, highlightthickness=0, bg=BACKGROUND_COLOR)
    canvas.grid(row=row, column=column, padx=padx)

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

class SearchBox:
    def __init__(self, container, row, column, width):
        self.placeholder = "Search..."
        self.entry = Entry(container, width=width, font=("Open Sans", 16), bg=LIGHT_BACKGROUND_COLOR, fg='white')
        self.entry.insert(0, self.placeholder)
        self.entry.grid(row=row, column=column, pady=10)

        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, END)

    def _add_placeholder(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)

class ScrollableFrame:
    def __init__(self, container):
        self.container = container

        self.border_frame = Frame(container, highlightbackground=UFC_RED, highlightthickness=3, background='orange')
        self.border_frame.grid(row=0, column=0, sticky="nsew")
        self.bounding_frame = Frame(self.border_frame, background=LIGHT_BACKGROUND_COLOR)
        self.bounding_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_frame = Frame(self.bounding_frame, width=15, bg=LIGHT_BACKGROUND_COLOR)
        self.scrollbar_frame.grid(row=0, column=1, sticky="ns")

        self.bounding_frame.grid_rowconfigure(0, weight=1)
        self.bounding_frame.grid_columnconfigure(0, weight=1)


        self.canvas = Canvas(self.bounding_frame, width=400, height=300, highlightthickness=0, background=LIGHT_BACKGROUND_COLOR)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", background=LIGHT_BACKGROUND_COLOR, troughcolor=LIGHT_BACKGROUND_COLOR)

        self.scrollbar = ttk.Scrollbar(self.scrollbar_frame, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.scrollbar.pack(fill="y", expand=True)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))


        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        self.list_frame = Frame(self.canvas, bg=LIGHT_BACKGROUND_COLOR)
        self.canvas_window = self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def _on_mousewheel(self, event):
            delta = int(-1 * (event.delta))
            top, bottom = self.canvas.yview()
            if(delta < 0 and top <= 0) or (delta > 0 and bottom >= 1):
                return
            
            self.canvas.yview_scroll(delta, "units")

    def _bind_mousewheel_to_children(self):
        def recursive_bind(widget):
            widget.bind("<MouseWheel>", self._on_mousewheel)
            for child in widget.winfo_children():
                recursive_bind(child)

        recursive_bind(self.list_frame)



    
class PaginatedList:
    def __init__(self, container, event_names=None):
        self.scrollable_frame = ScrollableFrame(container)
        self.page = 0
        self.event_names = event_names or []
        self.list_length = len(self.event_names)

        self.page_label = Label(container, bg=BACKGROUND_COLOR, fg='white', font=("Open Sans", 14))
        self.page_label.grid(row=1, column=0, pady=5)
        self.update_page_label()

        button_frame = Frame(container, bg=BACKGROUND_COLOR)
        create_canvas_button(button_frame, text="Previous", row=0, column=0, command=self.prev_page, width=80, height=30, font=("Open Sans", 14), padx=10)
        create_canvas_button(button_frame, text="Next", row=0, column=1, command=self.next_page, width=80, height=30, font=("Open Sans", 14), padx=10)
        button_frame.grid(row=2, column=0)

    def update_page_label(self):
        total_pages = math.ceil(self.list_length / LIST_ENTRIES_PER_PAGE)
        self.page_label.configure(text=f"Page {self.page + 1} of {total_pages}")

    def next_page(self):
        if (self.page + 1) * LIST_ENTRIES_PER_PAGE + 1 <= self.list_length:
            self.page += 1
            show_list_entries(self, self.page)
            self.scrollable_frame.canvas.yview_moveto(0.0)
            self.update_page_label()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            show_list_entries(self, self.page)
            self.scrollable_frame.canvas.yview_moveto(0.0)
            self.update_page_label()
            


def refresh_random_fight(container, app_state):
    app_state.get_random_fight(app_state.db_manager)

    clear_screen(container)

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

        create_canvas_button(container, "NEW FIGHT", 1, 0, lambda: refresh_random_fight(container, app_state), 120, 50)

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
    
def show_list_entries(list: PaginatedList, page, event_names = None):
    clear_screen(list.scrollable_frame.list_frame)

    if event_names is None:
        return
    
    start = page * LIST_ENTRIES_PER_PAGE
    end = start + LIST_ENTRIES_PER_PAGE
    for i in range(start, min(end, len(event_names))):
        Label(list.scrollable_frame.list_frame, text=event_names[i], bg='green', fg='white', font=("Open Sans", 16)).pack(anchor="w", padx=2, pady=(1,1))

    list.scrollable_frame._bind_mousewheel_to_children()
    list.scrollable_frame.canvas.update_idletasks()
    list.scrollable_frame.canvas.configure(scrollregion=list.scrollable_frame.canvas.bbox("all"))


    

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

    search_box = SearchBox(container, 2, 0, 30)

    events_frame = Frame(container, bg=BACKGROUND_COLOR)
    event_names = app_state.db_manager.get_all_events()
    events_list = PaginatedList(events_frame)
    show_list_entries(events_list, 0, event_names)

    def perform_search(event):
        query = search_box.entry.get().strip()
        if query == "" or query == search_box.placeholder:
            filtered = event_names
        else:
            filtered = [name for name in event_names if query.lower() in name.lower()]
        events_list.page = 0
        events_list.event_names = filtered
        events_list.list_length = len(filtered)
        events_list.update_page_label()
        show_list_entries(events_list, 0, filtered)

    search_box.entry.bind("<KeyRelease>", perform_search)

    events_frame.grid(row=3, column=0, pady=(20,10))

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