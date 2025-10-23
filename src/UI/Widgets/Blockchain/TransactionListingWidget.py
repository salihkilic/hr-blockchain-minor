from decimal import Decimal

from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Input

from Models import Transaction


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
            Static(f"Type: {self.transaction.kind}"),
            Static(f"Sender: {self.transaction.sender_address}"),
            Static(f"Receiver: {self.transaction.receiver_address}"),
            Static(f"Amount: {self.transaction.amount.quantize(Decimal('0.01'))} GCN"),
            Static(f"Fee: {self.transaction.fee.quantize(Decimal('0.01'))} GCN"),
            Vertical(
                Horizontal(
                    Button("Move to pool", classes="button"),
                    Button("Move to block", classes="button"),
                    classes="button_col"
                ),
                Horizontal(
                    Button("Show details", classes="button"),
                    classes="button_col"
                ),
                classes="button_row"
            ),
            title=f"TX {self.transaction.txid}",
            collapsed=True,
            classes=("transaction--reward" if self.transaction.kind == 'reward' else "")
        )
