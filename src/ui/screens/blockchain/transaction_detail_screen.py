from decimal import Decimal

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button, ListItem, Label, ListView, Rule

from models import Transaction


class TransactionDetailScreen(Screen):

    DEFAULT_CSS = """
        #close {
            margin: 2;
        }
        .transaction-detail-screen{
            margin: 2;
            padding: 1;
        }
        .tx-hash{
            text-style: bold;
        }
        .rule {
            color: orange;
        }
        Vertical {
            border: double orange;
        }
    """

    def __init__(self, transaction: Transaction):
        super().__init__()
        self.transaction = transaction

    def compose(self) -> ComposeResult:
        yield Button("Close", id="close")
        vertical = Vertical(
            Label(f"Transaction hash: {self.transaction.id}", classes="tx-hash"),
            Rule(line_style="double", classes="rule"),
            Label(f"Amount: {self.transaction.amount.quantize(Decimal('0.01'))} GCN"),
            Label(f"Fee: {self.transaction.fee.quantize(Decimal('0.01'))} GCN"),
            Rule(line_style="double", classes="rule"),
            Label(f"Created at: {self.transaction.timestamp}"),
            Label(f"Sender: {self.transaction.sender_public_key}"),
            Label(f"Receiver: {self.transaction.receiver_address}"),
            Label(f"Signature: {self.transaction.sender_signature}"),
            classes="transaction-detail-screen"
        )
        vertical.border_title = self.transaction.kind.value.upper()
        yield vertical
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()