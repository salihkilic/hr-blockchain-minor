from textual import events, log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Pool, Ledger
from events import BlockAddedFromNetworkEvent
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
            .alert--warning {
                background: orange 10%;
                padding: 1 1;
                margin: 0 0 1 0;
                text-align: center;
            }
        """

    transactions: list[Transaction] = reactive(lambda: Pool.get_instance().get_transaction_without_marked_for_block(), recompose=True)

    def __init__(self):
        super().__init__()

    def on_mount(self) -> None:
        Pool.subscribe(self.update_state)
        UserService.subscribe(self.update_state)


    def update_state(self, param):
        log("Transaction pool updated, refreshing transactions...")
        self.transactions = Pool.get_instance().get_transaction_without_marked_for_block()
        self.mutate_reactive(TransactionPoolWidget.transactions)


    def compose(self) -> ComposeResult:
        children = []

        if UserService.logged_in_user is not None:
            if Pool.get_instance().get_required_transactions() is not None:
                children.append(
                    Button("Add required transactions to block", classes="button button--add", id="add_required_txs")
                )
            elif len(Pool.get_instance().get_transactions()) > 0:
                children.append(
                    Static("Not enough transactions for block", classes="alert alert--warning")
                )

        txs = self.transactions
        txs.sort(key=lambda tx: tx.timestamp)

        children.append(
            VerticalScroll(
                *list(map(lambda tx: TransactionListingWidget(tx), txs)),
                classes="transactions_scroll"
            )
        )

        yield Vertical(
            *children
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "add_required_txs":
            required_txs = Pool.get_instance().get_required_transactions()
            if required_txs is not None:
                for tx in required_txs:
                    Pool.get_instance().mark_transaction_for_block(tx)