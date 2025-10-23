from pathlib import Path

from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Input

from Models import Transaction
from Models.Enum import TransactionType


class TransactionListingWidget(Widget):

    DEFAULT_CSS = """
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
            Static(f"Type: {self.transaction.tx_type.name}"),
            Static(f"Sender: {self.transaction.sender}"),
            Static(f"Receiver: {self.transaction.receiver}"),
            Static(f"Amount: {self.transaction.amount} GCN"),
            Horizontal(
                Button("Move to pool", id="move_to_pool"),
                Button("Show details", id="show_details"),
                classes="button_row"
            ),
            title=f"TX {self.transaction.tx_id}",
            collapsed=True,
            classes=("transaction--reward" if self.transaction.tx_type == TransactionType.REWARD else "")
        )


