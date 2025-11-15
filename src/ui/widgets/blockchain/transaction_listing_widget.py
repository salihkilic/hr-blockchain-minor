from decimal import Decimal
from typing import Optional

from textual import log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Input

from blockchain import Pool
from models import Transaction
from models.enum import TransactionType
from services.user_service import UserService
from ui.screens.blockchain.transaction_detail_screen import TransactionDetailScreen


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
        .transaction--invalid {
            background: red 80%;
        }
        .button_row {
            margin: 1 0;
        }
    """

    is_marked_for_block = reactive(False, recompose=True)
    can_be_moved = reactive(False, recompose=True)
    can_be_removed = reactive(False, recompose=True)

    def __init__(self, transaction: Transaction, show_move_buttons: bool = True):
        super().__init__()
        self.transaction = transaction
        self.set_reactive(TransactionListingWidget.is_marked_for_block, Pool.get_instance().get_transactions_marked_for_block().__contains__(self.transaction))
        self.set_reactive(TransactionListingWidget.can_be_moved, UserService.logged_in_user is not None)
        self.show_move_buttons = show_move_buttons and self.can_be_moved

    def on_mount(self):
        UserService.subscribe(self.update_can_be_moved)

    def update_can_be_moved(self, user):
        self.can_be_moved = user is not None

    def compose(self) -> ComposeResult:
        classes = ""

        can_be_canceled = True

        logged_in_user = UserService.logged_in_user

        if logged_in_user is not None:
            if self.transaction.sender_address != logged_in_user.address:
                can_be_canceled = False

        if self.transaction not in Pool.get_instance().get_transactions() or self.transaction in Pool.get_instance().get_transactions_marked_for_block():
            can_be_canceled = False

        if self.transaction.kind == TransactionType.MINING_REWARD or self.transaction.kind == TransactionType.SIGNUP_REWARD:
            classes = "transaction--reward"

        if self.transaction.is_invalid:
            classes = "transaction--invalid"

        move_buttons = []

        if self.show_move_buttons:
            move_buttons = [
                Horizontal(
                    Button("Move to pool", id="move_to_pool", classes="button", disabled=not self.is_marked_for_block or not self.can_be_moved),
                    Button("Move to block", id="move_to_block", classes="button", disabled=self.is_marked_for_block or not self.can_be_moved),
                    classes="button_col"
                ),
            ]

        other_buttons = [
            Horizontal(
                Button("Show details", classes="button", id="show_tx_details"),
                Button("Cancel transaction", classes="button", id="cancel_tx", disabled=not can_be_canceled),
                classes="button_col"
            ),
        ]

        yield Collapsible(
            Label(f"Type: {self.transaction.kind.value.upper()}"),
            Label(f"Sender: {self.transaction.sender_address}"),
            Label(f"Receiver: {self.transaction.receiver_address}"),
            Label(f"Amount: {self.transaction.amount.quantize(Decimal('0.01'))} GCN"),
            Label(f"Fee: {self.transaction.fee.quantize(Decimal('0.01'))} GCN"),
            Label(f"Created at: {self.transaction.timestamp_datetime.strftime("%d-%m-%Y %H:%M:%S")}"),
            Vertical(
                *move_buttons,
                *other_buttons,
                classes="button_row"
            ),
            title=f"TX {self.transaction.hash}",
            collapsed=True,
            classes=(classes)
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "show_tx_details":
            self.app.push_screen(TransactionDetailScreen(self.transaction))
        if event.button.id == "move_to_pool":
            from blockchain import Pool
            Pool.get_instance().unmark_transaction_for_block(self.transaction)
        if event.button.id == "move_to_block":
            from blockchain import Pool
            Pool.get_instance().mark_transaction_for_block(self.transaction)
        if event.button.id == "cancel_tx":
            from blockchain import Pool
            Pool.get_instance().remove_transaction(self.transaction)

