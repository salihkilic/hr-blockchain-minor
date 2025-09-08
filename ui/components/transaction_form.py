from __future__ import annotations

"""Transaction form component.

Responsibilities:
  - Render sender, recipient, amount inputs
  - Provide callback to add a transaction via controller
  - Trigger pending + status refresh callbacks

External callbacks expected (dict keys):
  refresh_pending() -> None
  set_status(message: str, color: tuple[int,int,int]) -> None
"""

def build_transaction_form(dpg, controller, callbacks, tags):
    tags['tx_sender'] = dpg.add_input_text(label="Sender", default_value="Alice")
    tags['tx_recipient'] = dpg.add_input_text(label="Recipient", default_value="Bob")
    tags['tx_amount'] = dpg.add_input_float(label="Amount", default_value=1.0, min_value=0.0)

    def add_tx_cb():
        s = dpg.get_value(tags['tx_sender']).strip()
        r = dpg.get_value(tags['tx_recipient']).strip()
        a = dpg.get_value(tags['tx_amount'])
        if not s or not r or a <= 0:
            callbacks['set_status']("Invalid transaction input", (255, 64, 64))
            return
        tx = controller.add_transaction(s, r, float(a))
        callbacks['set_status'](f"Added tx {tx.sender}->{tx.recipient} ({tx.amount})", (128, 255, 128))
        callbacks['refresh_pending']()

    dpg.add_button(label="Add Transaction", callback=add_tx_cb)

