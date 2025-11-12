from textual import events, log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Pool
from models import Transaction
from services.user_service import UserService
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
            .button--add {
                width: 100%;
                margin: 0 0 1 0;
            }
        """

    transactions: list[Transaction] = reactive(lambda: Pool.get_instance().get_transaction_without_marked_for_block(), recompose=True)
    show_add_required: bool = reactive(False, recompose=True)

    def __init__(self):
        super().__init__()

    def on_mount(self) -> None:
        Pool.subscribe(self.update_transactions)
        UserService.subscribe(self.update_show_add_required)


    def update_transactions(self, param):
        log("Transaction pool updated, refreshing transactions...")
        self.transactions = Pool.get_instance().get_transaction_without_marked_for_block()
        self.mutate_reactive(TransactionPoolWidget.transactions)

    def update_show_add_required(self, user):
        log("User state changed, updating show_add_required...")
        self.show_add_required = user is not None



    def compose(self) -> ComposeResult:

        children = []

        if self.show_add_required:
            children.append(
                Button("Add required transactions to block", classes="button button--add", id="add_required_txs")
            )

        children.append(
            VerticalScroll(
                *list(map(lambda tx: TransactionListingWidget(tx), self.transactions)),
                classes="transactions_scroll"
            )
        )

        yield Vertical(
            *children
        )
