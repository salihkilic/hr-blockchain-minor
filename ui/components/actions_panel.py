from __future__ import annotations
"""Actions panel component.
Provides mining and validation controls.
"""

def build_actions_panel(dpg, controller, callbacks):
    def mine_cb():
        if not controller.blockchain.pending_transactions:
            callbacks['set_status']("No pending transactions to mine", (200, 200, 100))
            return
        block = controller.mine()
        callbacks['set_status'](f"Mined block #{block.index} ({len(block.transactions)} txs)", (128, 200, 255))
        callbacks['refresh_chain']()
        callbacks['refresh_pending']()

    dpg.add_button(label="Mine Pending Transactions", callback=mine_cb)
    dpg.add_spacer(height=10)
    dpg.add_text("Validation")

    def validate_cb():
        valid = controller.is_valid()
        callbacks['set_status'](f"Chain valid: {valid}", (128, 255, 128) if valid else (255, 64, 64))

    dpg.add_button(label="Validate Chain", callback=validate_cb)

