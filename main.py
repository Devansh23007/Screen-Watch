import threading

import customtkinter as ctk

from engine import Engine
from ui import App

if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    engine = Engine()
    threading.Thread(target=engine.run_forever, daemon=True).start()
    App(engine).mainloop()
