from tkinter import *
import threading
from database.main import create_database
from database.manager import *
from ui import *

def start_loading_database(root, spinner):
    set_row_column_weights(root, rows=[0], columns=[0])
    def thread_target():
        create_database(lambda: root.after(0, lambda: finish_loading(root, spinner)))
    threading.Thread(target=thread_target, daemon=True).start()

def finish_loading(root, spinner):
    if spinner:
        spinner.stop()
    set_row_column_weights(root, rows=[0], row_weight=0)
    main_ui(root)

def on_close(db, root):
    db.close()
    root.destroy()

def launch_app():
    root = Tk()
    root.geometry("800x600")
    root.configure(bg=BACKGROUND_COLOR)
    root.title("UFC Database")

    frame = Frame(root, bg=BACKGROUND_COLOR)
    frame.grid(row=0, column=0)

    loading_text = Label(frame, text="Loading database", bg=BACKGROUND_COLOR, fg=ACCENT_COLOR, font=("Open Sans", 18))
    loading_text.grid(row=1)
    spinner = GIFSpinner(frame, "res/loading_spinner.gif", scale=0.5)

    db = DatabaseManager()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(db, root))
    start_loading_database(root, spinner)
    # finish_loading(root, spinner)       #for testing purposes
    root.mainloop()