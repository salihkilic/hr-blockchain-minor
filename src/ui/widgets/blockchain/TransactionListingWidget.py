from decimal import Decimal

from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Input

from models import Transaction
from ui.screens.blockchain.TransactionDetailScreen import TransactionDetailScreen


class TransactionListingWidget(Widget):
    DEFAULT_CSS = """
        .button_col {
            height: auto;
        }
        .button_row {
            height: auto;
        }
        .button {
            width: 50%;
        }
        TransactionListingWidget {
            height: auto;
        }
        .transaction--reward {
            background: green 10%;
        }
        .button_row {
            margin: 1 0;
        }
    """

    def __init__(self, transaction: Transaction):
        self.transaction = transaction
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Collapsible(
            Label(f"Type: {self.transaction.kind.upper()}"),
            Label(f"Sender: {self.transaction.sender_address}"),
            Label(f"Receiver: {self.transaction.receiver_address}"),
            Label(f"Amount: {self.transaction.amount.quantize(Decimal('0.01'))} GCN"),
            Label(f"Fee: {self.transaction.fee.quantize(Decimal('0.01'))} GCN"),
            Vertical(
                Horizontal(
                    Button("Move to pool", classes="button"),
                    Button("Move to block", classes="button"),
                    classes="button_col"
                ),
                Horizontal(
                    Button("Show details", classes="button", id="show_tx_details"),
                    classes="button_col"
                ),
                classes="button_row"
            ),
            title=f"TX {self.transaction.txid}",
            collapsed=True,
            classes=("transaction--reward" if self.transaction.kind == 'reward' else "")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "show_tx_details":
            self.app.push_screen(TransactionDetailScreen(self.transaction))