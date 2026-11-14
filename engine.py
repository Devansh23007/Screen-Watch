"""Background brain: watches the active window and analyzes on change."""
import queue
import threading
import time

import analyzer
import capture
import config
import memory
from privacy import is_blocked
from watcher import get_active_window, list_taskbar_apps


class Engine:
    def __init__(self):
        self.paused = False
        self.stop = threading.Event()
        self._last_key = None
        self._last_hash = None
        self._last_time = 0
        self.observations = queue.Queue()

    def run_forever(self):
        while not self.stop.is_set():
            try:
                self._tick()
            except Exception as e:           # never let the loop die
                print("watch error:", e)
            time.sleep(config.CHECK_INTERVAL)

    def _tick(self):
        if self.paused:
            return
        app, title = get_active_window()
        key = (app, title)
        if key == self._last_key:
            return
        if time.time() - self._last_time < config.MIN_SECONDS_BETWEEN_ANALYSES:
            return                            # try again next tick
        self._last_key = key

        if is_blocked(app, title):
            memory.save(app, "[private]", "Private window, not captured")
            return

        img, jpeg = capture.screenshot()
        h = capture.fingerprint(img)
        if self._last_hash is not None and (h - self._last_hash) <= config.SAME_SCREEN_THRESHOLD:
            return                            # screen looks the same, skip
        self._last_hash = h
        self._last_time = time.time()

        summary = analyzer.describe(jpeg, app, title, list_taskbar_apps())
        memory.save(app, title, summary)
        self.observations.put((app, title, summary))
        print(f"[{app}] {summary}\n")
        if config.SAVE_IMAGES:
            memory.save_image(jpeg)
            memory.cleanup_images()

    def ask(self, question):
        """Fresh screenshot + recent history -> answer."""
        app, title = get_active_window()
        if is_blocked(app, title):
            return "The active window is on your privacy blocklist, so I did not look at it."
        _, jpeg = capture.screenshot()
        return analyzer.ask(jpeg, app, title, question, memory.context_text(15))
