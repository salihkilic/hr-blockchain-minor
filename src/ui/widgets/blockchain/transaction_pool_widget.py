from textual import events, log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Pool
from models import Transaction
from .transaction_listing_widget import TransactionListingWidget


class TransactionPoolWidget(Widget):
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
        """

    transactions: list[Transaction] = reactive([], recompose=True)

    def __init__(self, ):
        super().__init__()
        self.transactions = Pool.get_instance().get_transactions()

    def on_mount(self) -> None:
        Pool.subscribe(self.update_transactions)

    def update_transactions(self, param):
        log("Updating transactions in pool widget")
        self.transactions = Pool.get_instance().get_transactions()

    def compose(self) -> ComposeResult:
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), self.transactions))

        yield Vertical(
            VerticalScroll(
                *txs_widgets,
                classes="transactions_scroll"
            ),
        )
