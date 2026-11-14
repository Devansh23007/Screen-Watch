"""SQLite history of what the user was doing (text only)."""
import os
import sqlite3
import time
from datetime import datetime

import config

os.makedirs(config.DATA_DIR, exist_ok=True)


def _conn():
    c = sqlite3.connect(config.DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, app TEXT, title TEXT, summary TEXT)""")
    return c


def save(app, title, summary):
    with _conn() as c:
        c.execute("INSERT INTO history(ts, app, title, summary) VALUES (?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), app, title, summary))


def recent(limit=15):
    with _conn() as c:
        rows = c.execute("SELECT ts, app, title, summary FROM history "
                         "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return rows[::-1]


def context_text(limit=15):
    return "\n".join(f"[{ts}] {app} - {title}: {summary}"
                     for ts, app, title, summary in recent(limit))


def save_image(jpeg):
    """Only used when config.SAVE_IMAGES is True."""
    os.makedirs(config.IMAGE_DIR, exist_ok=True)
    path = os.path.join(config.IMAGE_DIR, f"{int(time.time())}.jpg")
    with open(path, "wb") as f:
        f.write(jpeg)


def cleanup_images():
    if not os.path.isdir(config.IMAGE_DIR):
        return
    cutoff = time.time() - config.IMAGE_KEEP_DAYS * 86400
    for name in os.listdir(config.IMAGE_DIR):
        p = os.path.join(config.IMAGE_DIR, name)
        if os.path.getmtime(p) < cutoff:
            os.remove(p)
