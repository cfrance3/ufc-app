import tkinter as tk
import threading
from database.main import create_database
from ui import main_ui, GIFSpinner

def start_loading_database(root, spinner):
    def thread_target():
        create_database(lambda: root.after(0, lambda: finish_loading(root, spinner)))
    threading.Thread(target=thread_target, daemon=True).start()

def finish_loading(root, spinner):
    if spinner:
        spinner.stop()
    main_ui(root)

def launch_app():
    root = tk.Tk()
    root.geometry("800x600")
    root.configure(bg="#555454")
    root.title("UFC Database")

    spinner = GIFSpinner(root, "res/loading_spinner2.gif", scale=0.5)
    start_loading_database(root, spinner)

    root.mainloop()