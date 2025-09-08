# UI bootstrap exposing build_ui for the application entrypoint.
from __future__ import annotations

from controllers import BlockchainController


def build_ui():  # pragma: no cover - interactive UI not unit tested
    """Initialize and start the DearPyGui based blockchain explorer.

    If DearPyGui isn't installed, prints a helpful message and returns gracefully.
    """
    try:
        import dearpygui.dearpygui as dpg  # noqa: F401
    except ImportError:  # Friendly fallback
        print("DearPyGui not installed. Install with: pip install dearpygui")
        return

    # Deferred import to avoid static analysis false-positives and optional dependency at import time.
    from importlib import import_module
    explorer_mod = import_module('ui.views.explorer')

    controller = BlockchainController()

    dpg.create_context()
    dpg.create_viewport(title="Blockchain Explorer", width=1100, height=700)

    with dpg.font_registry():  # optional nicer default font size placeholder
        pass

    explorer_mod.create_blockchain_explorer(controller)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
