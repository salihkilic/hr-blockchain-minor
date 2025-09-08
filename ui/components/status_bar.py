from __future__ import annotations
"""Status bar component providing a simple status text area and helper."""

def build_status_bar(dpg):
    return dpg.add_text("Status: Ready", tag="status_text")


def set_status(dpg, message: str, color=(200, 200, 200)):
    try:
        dpg.configure_item("status_text", default_value=message, color=color)
    except Exception:
        pass

