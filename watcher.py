"""Finds out which app/window is active and which apps are running."""
import os
import subprocess
import sys

import psutil


def get_active_window():
    """Returns (app_name, window_title)."""
    try:
        if sys.platform == "win32":
            import win32gui
            import win32process
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name(), title

        if sys.platform == "darwin":
            from AppKit import NSWorkspace
            from Quartz import (CGWindowListCopyWindowInfo,
                                kCGNullWindowID, kCGWindowListOptionOnScreenOnly)
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            title = ""
            for w in CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID):
                if w.get("kCGWindowOwnerPID") == app.processIdentifier() and w.get("kCGWindowLayer") == 0:
                    title = w.get("kCGWindowName") or ""
                    break
            return app.localizedName() or "unknown", title

        # Linux (needs: sudo apt install xdotool)
        title = subprocess.check_output(["xdotool", "getactivewindow", "getwindowname"],
                                        text=True).strip()
        pid = int(subprocess.check_output(["xdotool", "getactivewindow", "getwindowpid"],
                                          text=True).strip())
        return psutil.Process(pid).name(), title
    except Exception:
        return "unknown", ""


def list_running_apps():
    names = {p.info["name"] for p in psutil.process_iter(["name"]) if p.info["name"]}
    return sorted(names)


def list_taskbar_apps():
    """Returns apps with visible top-level windows represented in the Windows taskbar."""
    if sys.platform != "win32":
        return []

    import win32con
    import win32gui
    import win32process

    names = set()

    def collect(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or not win32gui.GetWindowText(hwnd):
            return True
        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
            return True
        if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
            return True

        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            name = psutil.Process(pid).name()
            names.add(os.path.splitext(name)[0])
        except (psutil.Error, OSError):
            pass
        return True

    win32gui.EnumWindows(collect, None)
    return sorted(names, key=str.casefold)


if __name__ == "__main__":
    import time
    last = None
    while True:
        cur = get_active_window()
        if cur != last:
            print(cur)
            last = cur
        time.sleep(1)
