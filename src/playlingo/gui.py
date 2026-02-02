"""Simple GUI for PlayLingo: clipboard translator and SRT overlay monitor.

Provides:
- translate_clipboard(): read clipboard text and show translation
- SRTMonitor: monitor an .srt file and show translated subtitle in an overlay window
- main(): start a small Tkinter app where user can paste text, translate, or monitor SRT

This implementation keeps GUI logic separated from pure logic so unit tests can exercise parsing and selection.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Iterable, Optional

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:  # pragma: no cover - platform GUI may not be available in test env
    tk = None

from .translator import translate
from .subtitles import srt_to_subs
from .logging_config import setup_logging, get_memory_handler, dump_logs_to_file
import sys, platform

logger = logging.getLogger(__name__)

from pathlib import Path
import json

# Default overlay appearance
DEFAULT_OVERLAY_SETTINGS = {
    "bg": "#000000",
    "fg": "#ffffff",
    "font_family": "Helvetica",
    "font_size": 20,
    "alpha": 1.0,
}

_CONFIG_PATH = Path.home() / ".playlingo_overlay.json"

def load_overlay_settings(path: Optional[Path] = None) -> dict:
    p = path or _CONFIG_PATH
    try:
        if p.exists():
            with p.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
                return {**DEFAULT_OVERLAY_SETTINGS, **data}
    except Exception:
        logger.exception("Failed to load overlay settings from %s", p)
    return {**DEFAULT_OVERLAY_SETTINGS}


def save_overlay_settings(settings: dict, path: Optional[Path] = None) -> None:
    p = path or _CONFIG_PATH
    try:
        with p.open("w", encoding="utf-8") as fh:
            json.dump(settings, fh, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to save overlay settings to %s", p)


def validate_overlay_settings(settings: dict) -> dict:
    """Validate and normalize overlay settings; returns a cleaned dict or raises ValueError."""
    out = dict(DEFAULT_OVERLAY_SETTINGS)
    if not isinstance(settings, dict):
        raise ValueError("settings must be a dict")

    if "bg" in settings:
        out["bg"] = str(settings["bg"]) or DEFAULT_OVERLAY_SETTINGS["bg"]
    if "fg" in settings:
        out["fg"] = str(settings["fg"]) or DEFAULT_OVERLAY_SETTINGS["fg"]
    if "font_family" in settings:
        out["font_family"] = str(settings["font_family"]) or DEFAULT_OVERLAY_SETTINGS["font_family"]
    if "font_size" in settings:
        try:
            out["font_size"] = int(settings["font_size"])
        except Exception:
            raise ValueError("font_size must be an integer")
    if "alpha" in settings:
        try:
            a = float(settings["alpha"])
            if not (0.0 <= a <= 1.0):
                raise ValueError("alpha must be between 0.0 and 1.0")
            out["alpha"] = a
        except Exception:
            raise ValueError("alpha must be a float between 0.0 and 1.0")
    return out


def _to_seconds(v):
    # Accept datetime.timedelta or float and convert to seconds (float)
    try:
        return float(v.total_seconds())
    except Exception:
        return float(v)


def find_current_subtitle(subs: Iterable[dict], elapsed: float) -> Optional[str]:
    """Return the subtitle text that should be active at `elapsed` seconds (float), or None.

    `subs` expected to be an iterable of dicts with keys: start, end, text
    start/end may be datetime.timedelta (from `srt`) or floats — both are supported.
    """
    for s in subs:
        start_s = _to_seconds(s["start"])
        end_s = _to_seconds(s["end"])
        if start_s <= elapsed <= end_s:
            return s.get("text") or None
    return None


class OverlayWindow:
    """An always-on-top simple overlay to show translated text.

    The appearance (bg/fg font/alpha) is loaded from configuration and can be
    adjusted via the SettingsWindow.
    """

    def __init__(self, settings: Optional[dict] = None):
        if tk is None:
            raise RuntimeError("tkinter is required for the GUI")
        self.settings = validate_overlay_settings(settings or load_overlay_settings())
        self.root = tk.Toplevel()
        self.root.title("PlayLingo Overlay")
        self.root.attributes("-topmost", True)
        # remove window decorations
        self.root.overrideredirect(True)
        self.label = tk.Label(
            self.root,
            text="",
            bg=self.settings["bg"],
            fg=self.settings["fg"],
            font=(self.settings["font_family"], self.settings["font_size"]),
            padx=10,
            pady=5,
        )
        self.label.pack()
        # transparency
        try:
            self.root.attributes("-alpha", float(self.settings.get("alpha", 1.0)))
        except Exception:
            logger.exception("Failed to set overlay alpha %s", self.settings.get("alpha"))
        # start hidden
        self.root.withdraw()

    def apply_settings(self, settings: dict):
        settings = validate_overlay_settings(settings)
        self.settings = settings
        self.label.config(bg=settings["bg"], fg=settings["fg"], font=(settings["font_family"], settings["font_size"]))
        try:
            self.root.attributes("-alpha", float(settings.get("alpha", 1.0)))
        except Exception:
            logger.exception("Failed to set overlay alpha %s", settings.get("alpha"))
        save_overlay_settings(settings)

    def show(self, text: str):
        logger.debug("Showing overlay: %s", text)
        self.label.config(text=text)
        self.root.update_idletasks()
        self.root.deiconify()

    def hide(self):
        logger.debug("Hiding overlay")
        self.root.withdraw()


class SRTMonitor:
    """Monitor an SRT file and show translated subtitles in an overlay window.

    Usage:
        monitor = SRTMonitor('subs.srt')
        monitor.start()
        monitor.play()    # starts playback anchored to current time
        monitor.stop()

    For testability the monitor accepts a `time_fn` that returns current time in seconds.
    """

    def __init__(self, filepath: str, translate_fn: Callable[[str, str, str], str] = translate, overlay: Optional[OverlayWindow] = None, poll_interval: float = 0.25, time_fn: Callable[[], float] = time.time):
        self.filepath = filepath
        self.translate_fn = translate_fn
        self.poll_interval = poll_interval
        self._time_fn = time_fn
        self._stop_ev = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._subs = []
        self._overlay = overlay
        self._play_start_real: Optional[float] = None
        self._play_offset: float = 0.0  # seconds offset between subtitle timestamps and real time

    def _load_subs(self):
        try:
            self._subs = srt_to_subs(self.filepath)
            logger.debug("Loaded %d subtitles from %s", len(self._subs), self.filepath)
        except Exception:
            logger.exception("Failed to load subs from %s", self.filepath)
            self._subs = []

    def start(self):
        self._stop_ev.clear()
        self._load_subs()
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        logger.info("SRTMonitor started for %s", self.filepath)

    def stop(self):
        self._stop_ev.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        logger.info("SRTMonitor stopped")

    def play(self, start_at_real_time: Optional[float] = None, offset: float = 0.0):
        """Start playback mapping subtitle timestamp 0 -> start_at_real_time (default now) + offset."""
        self._play_start_real = start_at_real_time if start_at_real_time is not None else self._time_fn()
        self._play_offset = offset
        logger.info("Playback started at real time %s with offset %s", self._play_start_real, self._play_offset)

    def _run(self):
        last_text = None
        while not self._stop_ev.is_set():
            # reload file in case it changed
            self._load_subs()
            if self._play_start_real is not None and self._subs:
                elapsed = (self._time_fn() - self._play_start_real) + self._play_offset
                current = find_current_subtitle(self._subs, elapsed)
                if current != last_text:
                    last_text = current
                    if current:
                        try:
                            translated = self.translate_fn(current, "auto", "en")
                        except Exception:
                            logger.exception("Translation failed for: %s", current)
                            translated = "[translation error]"
                        if self._overlay:
                            self._overlay.show(translated)
                    else:
                        if self._overlay:
                            self._overlay.hide()
            time.sleep(self.poll_interval)


def translate_clipboard(root: tk.Tk):
    try:
        text = root.clipboard_get()
    except Exception:
        messagebox.showinfo("PlayLingo", "No text in clipboard")
        return
    if not text.strip():
        messagebox.showinfo("PlayLingo", "Clipboard is empty")
        return
    translated = translate(text, "auto", "en")
    # show a small popup
    popup = tk.Toplevel(root)
    popup.title("Translation")
    popup.attributes("-topmost", True)
    label = tk.Label(popup, text=translated, padx=10, pady=10, wraplength=400)
    label.pack()
    # auto-close after 5s
    popup.after(5000, popup.destroy)


def main():
    if tk is None:
        raise RuntimeError("tkinter is required for the GUI")

    # Setup logging early. Use debug if env var set.
    import os

    level = logging.DEBUG if os.environ.get("PLAYLINGO_DEBUG") in ("1", "true", "True") else logging.INFO
    setup_logging(level=level, capture_in_memory=True, memory_capacity=500)

    root = tk.Tk()
    root.title("PlayLingo")

    frm = tk.Frame(root, padx=10, pady=10)
    frm.pack()

    text_label = tk.Label(frm, text="Text to translate:")
    text_label.grid(row=0, column=0, sticky="w")
    text_entry = tk.Text(frm, height=4, width=60)
    text_entry.grid(row=1, column=0, columnspan=3)

    def on_translate():
        text = text_entry.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("PlayLingo", "Enter text to translate")
            return
        translated = translate(text, "auto", "en")
        messagebox.showinfo("PlayLingo", translated)

    def open_settings():
        nonlocal overlay
        if tk is None:
            return
        # create overlay if not exists so settings can be previewed
        if not overlay:
            overlay = OverlayWindow()
        SettingsWindow(root, overlay)

    settings_btn = tk.Button(frm, text="Settings", command=open_settings)
    settings_btn.grid(row=2, column=2, pady=6)

    def open_diagnostics():
        nonlocal overlay
        try:
            mh = get_memory_handler()
            if mh is None:
                messagebox.showinfo("Diagnostics", "In-memory logging not active")
                return
            DiagnosticsWindow(root, mh)
        except Exception:
            logger.exception("Failed to open diagnostics window")
            messagebox.showerror("Diagnostics", "Failed to open diagnostics window")

    diag_btn = tk.Button(frm, text="Diagnostics", command=open_diagnostics)
    diag_btn.grid(row=2, column=3, pady=6)

    # install crash handler for main window
    try:
        from .diagnostics import install_crash_handler

        def _report_cb(p):
            messagebox.showinfo("Diagnostics", f"Collected diagnostics to: {p}")

        install_crash_handler(root, report_callback=_report_cb)
    except Exception:
        logger.exception("Failed to install crash handler")

    translate_btn = tk.Button(frm, text="Translate", command=on_translate)
    translate_btn.grid(row=2, column=0, pady=6)

    clipboard_btn = tk.Button(frm, text="Translate Clipboard", command=lambda: translate_clipboard(root))
    clipboard_btn.grid(row=2, column=1, pady=6)

    # SRT monitor UI
    srt_label = tk.Label(frm, text="Subtitle file (.srt):")
    srt_label.grid(row=3, column=0, sticky="w")
    srt_entry = tk.Entry(frm, width=50)
    srt_entry.grid(row=4, column=0, columnspan=2, sticky="w")

    def browse():
        path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt"), ("All files", "*")])
        if path:
            srt_entry.delete(0, tk.END)
            srt_entry.insert(0, path)

    browse_btn = tk.Button(frm, text="Browse", command=browse)
    browse_btn.grid(row=4, column=2, sticky="w")

    overlay = None
    monitor = None

    def on_start_monitor():
        nonlocal overlay, monitor
        path = srt_entry.get().strip()
        if not path:
            messagebox.showinfo("PlayLingo", "Select an SRT file to monitor")
            return
        if not overlay:
            overlay = OverlayWindow()
        if monitor:
            monitor.stop()
        monitor = SRTMonitor(path, overlay=overlay)
        monitor.start()
        monitor.play()
        messagebox.showinfo("PlayLingo", "Started monitoring. Use Play/Stop to control playback.")

    # Settings window class (keeps GUI code grouped)
    class SettingsWindow(tk.Toplevel):
        def __init__(self, parent: tk.Tk, overlay: OverlayWindow):
            super().__init__(parent)
            self.title("Overlay Settings")
            self.overlay = overlay
            self.transient(parent)
            self.resizable(False, False)

            s = overlay.settings

            tk.Label(self, text="Background (e.g. #000000):").grid(row=0, column=0, sticky="w")
            self.bg_entry = tk.Entry(self)
            self.bg_entry.insert(0, s["bg"])
            self.bg_entry.grid(row=0, column=1)
            tk.Button(self, text="Pick", command=self.pick_bg).grid(row=0, column=2)

            tk.Label(self, text="Foreground (e.g. #ffffff):").grid(row=1, column=0, sticky="w")
            self.fg_entry = tk.Entry(self)
            self.fg_entry.insert(0, s["fg"])
            self.fg_entry.grid(row=1, column=1)
            tk.Button(self, text="Pick", command=self.pick_fg).grid(row=1, column=2)

            tk.Label(self, text="Font family:").grid(row=2, column=0, sticky="w")
            self.font_entry = tk.Entry(self)
            self.font_entry.insert(0, s["font_family"])
            self.font_entry.grid(row=2, column=1)

            tk.Label(self, text="Font size:").grid(row=3, column=0, sticky="w")
            self.size_entry = tk.Entry(self)
            self.size_entry.insert(0, str(s["font_size"]))
            self.size_entry.grid(row=3, column=1)

            tk.Label(self, text="Transparency (0.0 - 1.0):").grid(row=4, column=0, sticky="w")
            self.alpha_entry = tk.Entry(self)
            self.alpha_entry.insert(0, str(s["alpha"]))
            self.alpha_entry.grid(row=4, column=1)

            save_btn = tk.Button(self, text="Save", command=self.on_save)
            save_btn.grid(row=5, column=0, pady=6)
            close_btn = tk.Button(self, text="Close", command=self.destroy)
            close_btn.grid(row=5, column=1, pady=6)

        def pick_bg(self):
            try:
                from tkinter import colorchooser

                c = colorchooser.askcolor(initialcolor=self.bg_entry.get())
                if c and c[1]:
                    self.bg_entry.delete(0, tk.END)
                    self.bg_entry.insert(0, c[1])
            except Exception:
                messagebox.showinfo("PlayLingo", "Color chooser not available")

        def pick_fg(self):
            try:
                from tkinter import colorchooser

                c = colorchooser.askcolor(initialcolor=self.fg_entry.get())
                if c and c[1]:
                    self.fg_entry.delete(0, tk.END)
                    self.fg_entry.insert(0, c[1])
            except Exception:
                messagebox.showinfo("PlayLingo", "Color chooser not available")

        def on_save(self):
            new = {
                "bg": self.bg_entry.get().strip(),
                "fg": self.fg_entry.get().strip(),
                "font_family": self.font_entry.get().strip(),
                "font_size": int(self.size_entry.get().strip()),
                "alpha": float(self.alpha_entry.get().strip()),
            }
            try:
                self.overlay.apply_settings(new)
                messagebox.showinfo("PlayLingo", "Settings saved")
            except Exception as e:
                messagebox.showerror("PlayLingo", f"Invalid settings: {e}")

    # Diagnostics window
    class DiagnosticsWindow(tk.Toplevel):
        def __init__(self, parent: tk.Tk, memory_handler):
            super().__init__(parent)
            self.title("Diagnostics")
            self.transient(parent)
            self.resizable(True, True)

            self.memory_handler = memory_handler

            tk.Label(self, text="Recent logs:").pack(anchor="w")
            self.text = tk.Text(self, width=100, height=20)
            self.text.pack(fill="both", expand=True)

            frm = tk.Frame(self)
            frm.pack(fill="x")
            tk.Button(frm, text="Refresh", command=self.refresh).pack(side="left")
            tk.Button(frm, text="Save to file", command=self.save).pack(side="left")
            tk.Button(frm, text="Collect & Zip", command=self.collect_zip).pack(side="left")
            tk.Button(frm, text="Send report", command=self.send_report).pack(side="left")
            tk.Button(frm, text="Create issue", command=self.create_issue).pack(side="left")
            tk.Button(frm, text="Copy", command=self.copy).pack(side="left")

            tk.Label(self, text="System info:").pack(anchor="w")
            self.info = tk.Text(self, width=100, height=6)
            self.info.pack(fill="both", expand=False)
            self.refresh()
            self._fill_info()

        def refresh(self):
            self.text.delete("1.0", tk.END)
            logs = self.memory_handler.get_logs()
            for l in logs:
                self.text.insert(tk.END, l + "\n")

        def save(self):
            fn = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log"), ("Text", "*.txt")])
            if not fn:
                return
            dump_logs_to_file(fn)
            messagebox.showinfo("Diagnostics", f"Saved logs to {fn}")

        def copy(self):
            try:
                s = self.text.get("1.0", tk.END)
                self.clipboard_clear()
                self.clipboard_append(s)
                messagebox.showinfo("Diagnostics", "Copied logs to clipboard")
            except Exception:
                messagebox.showerror("Diagnostics", "Failed to copy to clipboard")

        def collect_zip(self):
            try:
                from .diagnostics import collect_diagnostics_zip

                p = collect_diagnostics_zip()
                messagebox.showinfo("Diagnostics", f"Collected diagnostics to: {p}")
            except Exception:
                logger.exception("Failed to collect diagnostics zip")
                messagebox.showerror("Diagnostics", "Failed to collect diagnostics")

        def send_report(self):
            try:
                url = tk.simpledialog.askstring("Send report", "Report URL:")
                if not url:
                    return
                import threading
                from .diagnostics import send_report

                def _send():
                    try:
                        res = send_report(url)
                        messagebox.showinfo("Send report", f"Report sent: {res}")
                    except Exception as e:
                        logger.exception("Failed to send report")
                        messagebox.showerror("Send report", f"Failed: {e}")

                threading.Thread(target=_send, daemon=True).start()
            except Exception:
                logger.exception("Failed to launch send_report")
                messagebox.showerror("Send report", "Failed to start report send")

        def create_issue(self):
            try:
                repo = tk.simpledialog.askstring("Create issue", "Repository (owner/repo):")
                if not repo:
                    return
                title = tk.simpledialog.askstring("Create issue", "Issue title:") or "PlayLingo Diagnostics Report"
                body = tk.simpledialog.askstring("Create issue", "Issue body (optional):") or ""

                import threading
                from .diagnostics import create_github_issue_with_diagnostics

                def _create():
                    try:
                        res = create_github_issue_with_diagnostics(repo, title=title, body=body)
                        messagebox.showinfo("Create issue", f"Issue created: {res}")
                    except Exception as e:
                        logger.exception("Failed to create issue")
                        messagebox.showerror("Create issue", f"Failed: {e}")

                threading.Thread(target=_create, daemon=True).start()
            except Exception:
                logger.exception("Failed to start create issue")
                messagebox.showerror("Create issue", "Failed to start")

        def _fill_info(self):
            self.info.delete("1.0", tk.END)
            self.info.insert(tk.END, f"Platform: {platform.platform()}\n")
            self.info.insert(tk.END, f"Python: {sys.version}\n")


    def on_stop_monitor():
        nonlocal monitor, overlay
        if monitor:
            monitor.stop()
            monitor = None
        if overlay:
            overlay.hide()

    start_btn = tk.Button(frm, text="Start Monitor", command=on_start_monitor)
    start_btn.grid(row=5, column=0, pady=6)

    stop_btn = tk.Button(frm, text="Stop Monitor", command=on_stop_monitor)
    stop_btn.grid(row=5, column=1, pady=6)

    root.mainloop()


if __name__ == "__main__":
    main()
