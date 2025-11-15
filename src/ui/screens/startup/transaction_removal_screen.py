import time
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.screen import Screen
from textual.widgets import Footer, Label, LoadingIndicator

from models import Transaction
from models.dto import UIAlert
from models.enum import AlertType
from services.user_service import UserService
from ui.screens.utils.alert_screen import AlertScreen

class TransactionRemovalScreen(Screen):

    DEFAULT_CSS = """
        Button {
            margin: 0 2;
        }
        TransactionRemovalScreen{
            margin: 2;
            padding: 1;
        }
        Input {
            margin: 1 2;
        }
        Label {
            margin: 0 2;
        }
        Container {
            height: 10;
            width: 100%;
        }
        .title{
            margin: 2;
            padding: 1;
            background: blue;
            width: 100%;
            text-align: center;
        }

    """

    def __init__(self):
        super().__init__()
        self.timer = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Removing your invalid transactions", classes="title"),
            Container(
                LoadingIndicator(),
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        self._validate_ledger()

    @work(exclusive=True, thread=True)
    def _validate_ledger(self):
        from blockchain import Pool

        user = UserService.logged_in_user
        invalid_transactions = Pool.get_instance().get_invalid_transactions_for_sender_address(user.address)

        if len(invalid_transactions) > 0:
            for tx in invalid_transactions:
                Pool.get_instance().remove_transaction(tx)
            self.app.call_from_thread(lambda: self.show_invalid_transaction_removed(invalid_transactions))
            return


            # success case
        self.app.call_from_thread(self.show_no_invalid_transactions)


    def show_no_invalid_transactions(self):
        from events import LoginValidationCompletedEvent
        LoginValidationCompletedEvent.dispatch()
        self.app.switch_screen(AlertScreen(UIAlert(
            title="No invalid transactions found",
            message="No invalid transactions were found in the transaction pool sent by you.",
            alert_type=AlertType.SUCCESS
        )))

    def show_invalid_transaction_removed(self, invalid_transactions: list[Transaction]):
        tx_list = "\n".join([f"- {tx.hash}" for tx in invalid_transactions])
        from events import LoginValidationCompletedEvent
        LoginValidationCompletedEvent.dispatch()
        self.app.switch_screen(AlertScreen(UIAlert(
            title="Automatically removed invalid transactions",
            message=f"The following transactions were found to be invalid and have been removed from your transaction pool:\n{tx_list}",
            alert_type=AlertType.WARNING,
            dismissed_automatically=False
        )))