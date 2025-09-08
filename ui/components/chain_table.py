from __future__ import annotations
"""Chain table component.
Provides creation + refresh logic for the blockchain table view.
"""

def build_chain_table(dpg):
    with dpg.table(tag="chain_table", header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp):
        dpg.add_table_column(label="#")
        dpg.add_table_column(label="Hash")
        dpg.add_table_column(label="Prev Hash")
        dpg.add_table_column(label="Tx Count")
        dpg.add_table_column(label="Nonce")


def refresh_chain_table(dpg, controller):
    # Clear existing rows - slot 1 holds row children
    for child in dpg.get_item_children("chain_table", 1) or []:
        dpg.delete_item(child)
    for block in controller.get_chain():
        with dpg.table_row(parent="chain_table"):
            dpg.add_text(str(block['index']))
            dpg.add_text(block['hash'][:16] + '…')
            dpg.add_text(block['previous_hash'][:16] + '…')
            dpg.add_text(str(len(block['transactions'])))
            dpg.add_text(str(block['nonce']))

