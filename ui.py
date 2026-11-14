"""Tray icon + chat window."""
import queue
import threading

import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw


def _icon_image():
    img = Image.new("RGB", (64, 64), "#1f6feb")
    d = ImageDraw.Draw(img)
    d.ellipse((14, 14, 50, 50), fill="white")
    d.ellipse((25, 25, 39, 39), fill="#1f6feb")
    return img


class App(ctk.CTk):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.q = queue.Queue()
        self.title("Screen Assistant")
        self.geometry("460x560")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)   # X hides to tray

        self.box = ctk.CTkTextbox(self, wrap="word", state="disabled")
        self.box.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        row = ctk.CTkFrame(self)
        row.pack(fill="x", padx=10, pady=(0, 10))
        self.entry = ctk.CTkEntry(row, placeholder_text="Ask about your screen...")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda e: self.send())
        ctk.CTkButton(row, text="Send", width=70, command=self.send).pack(side="right")

        self._add("Assistant", "I'm watching your screen. Ask me anything.\n"
                               "(This window hides for a moment while I look.)")
        self._start_tray()
        self.after(200, self._poll)

    # ---------- chat ----------
    def _add(self, who, text):
        self.box.configure(state="normal")
        self.box.insert("end", f"{who}: {text}\n\n")
        self.box.configure(state="disabled")
        self.box.see("end")

    def send(self):
        question = self.entry.get().strip()
        if not question:
            return
        self.entry.delete(0, "end")
        self._add("You", question)
        self.withdraw()                                   # so it isn't in the screenshot
        self.after(400, lambda: threading.Thread(
            target=self._work, args=(question,), daemon=True).start())

    def _work(self, question):
        try:
            answer = self.engine.ask(question)
        except Exception as e:
            answer = f"Error: {e}"
        self.q.put(("answer", answer))

    # ---------- tray ----------
    def _start_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Open chat", lambda: self.q.put(("show", None)), default=True),
            pystray.MenuItem(lambda item: "Resume watching" if self.engine.paused else "Pause watching",
                             self._toggle_pause),
            pystray.MenuItem("Quit", lambda: self.q.put(("quit", None))),
        )
        self.tray = pystray.Icon("screen-assistant", _icon_image(), "Screen Assistant", menu)
        self.tray.run_detached()

    def _toggle_pause(self):
        self.engine.paused = not self.engine.paused
        self.tray.title = "Screen Assistant (paused)" if self.engine.paused else "Screen Assistant"
        self.tray.update_menu()

    # ---------- main-thread message pump ----------
    def _poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "answer":
                    self._add("Assistant", data)
                    self.deiconify(); self.lift()
                elif kind == "show":
                    self.deiconify(); self.lift()
                elif kind == "quit":
                    self.engine.stop.set()
                    self.tray.stop()
                    self.destroy()
                    return
        except queue.Empty:
            pass
        try:
            while True:
                app, title, summary = self.engine.observations.get_nowait()
                self._add("Screen", f"{app} - {title}\n{summary}")
        except queue.Empty:
            pass
        self.after(200, self._poll)
