from tkinter import *
import threading
from database.main import create_database
from database.manager import *
from ui import *

class AppState:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_fight = None
        self.current_page = None

def start_loading_database(root, db_manager, spinner):
    set_row_column_weights(root, rows=[0], columns=[0])
    def thread_target():
        create_database(lambda: root.after(0, lambda: finish_loading(root, db_manager, spinner)))
    threading.Thread(target=thread_target, daemon=True).start()

def finish_loading(root, db_manager, spinner):
    if spinner:
        spinner.stop()
    set_row_column_weights(root, rows=[0], row_weight=0, columns=[0])
    main_page(root, AppState(db_manager))

def on_close(db, root):
    db.close()
    root.destroy()

def launch_app():
    root = Tk()
    root.geometry("800x600")
    root.minsize(600, 400)
    root.configure(bg=BACKGROUND_COLOR)
    root.title("UFC Database")

    root.lift()
    root.focus_force()

    loading_frame = Frame(root, bg=BACKGROUND_COLOR)
    loading_frame.grid(row=0, column=0)

    loading_text = Label(loading_frame, text="Loading database", bg=BACKGROUND_COLOR, fg=ACCENT_COLOR, font=("Open Sans", 18))
    loading_text.grid(row=1)
    spinner = GIFSpinner(loading_frame, "res/loading_spinner.gif", scale=0.5)

    db_manager = DatabaseManager()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(db_manager, root))
    # start_loading_database(root, db_manager, spinner)
    finish_loading(root, db_manager, spinner)       #for testing purposes
    root.mainloop()