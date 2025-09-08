from __future__ import annotations
"""Pending transactions list component."""

def build_pending_list(dpg):
    return dpg.add_listbox(items=[], num_items=8, tag="pending_txs")


def refresh_pending_list(dpg, controller):
    items = [f"{tx.sender[:6]}->{tx.recipient[:6]} {tx.amount}" for tx in controller.blockchain.pending_transactions]
    dpg.configure_item("pending_txs", items=items)

