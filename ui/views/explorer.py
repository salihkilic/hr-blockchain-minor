from __future__ import annotations

from ui.components import (
    build_transaction_form,
    build_pending_list,
    refresh_pending_list,
    build_chain_table,
    refresh_chain_table,
    build_actions_panel,
    build_status_bar,
    set_status,
)


def create_blockchain_explorer(controller):  # pragma: no cover - UI glue
    """Compose the blockchain explorer window from modular components."""
    import dearpygui.dearpygui as dpg

    # Callback helpers -------------------------------------------------------
    def refresh_chain():
        refresh_chain_table(dpg, controller)

    def refresh_pending():
        refresh_pending_list(dpg, controller)

    def set_status_cb(message: str, color=(200, 200, 200)):
        set_status(dpg, message, color)

    callbacks = {
        'refresh_chain': refresh_chain,
        'refresh_pending': refresh_pending,
        'set_status': set_status_cb,
    }

    tags = {}

    # Layout -----------------------------------------------------------------
    with dpg.window(label="Blockchain Explorer", tag="main_window", width=-1, height=-1):
        dpg.add_text("Demo Educational Blockchain - Not for Production Use", color=(200, 180, 0))
        dpg.add_separator()

        with dpg.group(horizontal=True):
            # Left column: transaction form + pending list
            with dpg.child_window(width=350, height=500, border=True):
                dpg.add_text("New Transaction")
                build_transaction_form(dpg, controller, callbacks, tags)
                dpg.add_separator()
                dpg.add_text("Pending Transactions")
                build_pending_list(dpg)

            # Right column: chain + actions tabs
            with dpg.child_window(width=-1, height=500, border=True):
                with dpg.tab_bar():
                    with dpg.tab(label="Chain"):
                        dpg.add_button(label="Refresh Chain", callback=lambda: refresh_chain())
                        build_chain_table(dpg)
                    with dpg.tab(label="Actions"):
                        build_actions_panel(dpg, controller, callbacks)

        dpg.add_separator()
        build_status_bar(dpg)

    # Initial population
    refresh_chain()
    refresh_pending()
