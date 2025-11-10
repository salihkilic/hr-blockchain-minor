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
        log(f"TransactionPoolWidget received pool update, current transaction count is {len(Pool.get_instance().get_transactions())}")
        self.transactions = Pool.get_instance().get_transactions()
        log(f"TransactionPoolWidget updated transactions, new count is {len(self.transactions)}")


    def compose(self) -> ComposeResult:

        yield Vertical(
            VerticalScroll(
                *list(map(lambda tx: TransactionListingWidget(tx), self.transactions)),
                classes="transactions_scroll"
            ),
        )
