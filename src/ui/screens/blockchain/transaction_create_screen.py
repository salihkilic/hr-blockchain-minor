from decimal import Decimal

from textual import log
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button, ListItem, Label, ListView, Rule

from exceptions.transaction import InvalidTransactionException, InsufficientBalanceException
from models import Transaction
from models.dto import UIAlert
from models.enum import AlertType
from services.user_service import UserService
from ui.screens.utils import AlertScreen


class TransactionCreateScreen(Screen):
    DEFAULT_CSS = """
        Button {
            margin: 2;
        }
        TransactionCreateScreen{
            margin: 2;
            padding: 1;
        }
        Input {
            margin: 1 2;
        }
        Label {
            margin: 0 2;
        }
        .tx_error{
            color: red;
            margin: 2 2;
        }
        .balance {
            margin: 1 2;
            text-style: bold;
        }
        .balance--warning {
            color: orange;
        }
    """

    tx_errors: list = reactive([], recompose=True)
    to = reactive("")
    amount = reactive(Decimal("0.0"))
    fee = reactive(Decimal("0.0"))

    def __init__(self):
        super().__init__()
        self.tx_errors = []  # reset per instance
        self.to = ""
        self.amount = Decimal("0.0")
        self.fee = Decimal("0.0")

    def compose(self) -> ComposeResult:
        log("Composing TransactionCreateScreen with errors: ", self.tx_errors)
        error_labels = [Label(f"{error}", classes="tx_error") for error in self.tx_errors]

        yield Vertical(
            *error_labels,
            Label("Create a new transaction"),
            Input(placeholder="To (username)", id="to"),
            Input(placeholder="Amount", id="amount"),
            Input(placeholder="Fee", id="fee"),
            Horizontal(
                Button("Create", id="create"),
                Button("Cancel", id="close"),
                classes="button-row",
            ),
        )
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "to":
            self.to = event.value
        if event.input.id == "amount":
            try:
                self.amount = Decimal(event.value)
            except:
                self.amount = Decimal("0.0")
        if event.input.id == "fee":
            try:
                self.fee = Decimal(event.value)
            except:
                self.fee = Decimal("0.0")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.tx_errors = []
            self.mutate_reactive(TransactionCreateScreen.tx_errors)
            self.app.pop_screen()
        if event.button.id == "create":
            self._create_transaction()

    def _create_transaction(self):
        self.tx_errors = []

        if not self.to:
            self.tx_errors.append("Recipient address is required.")

        if self.amount <= 0:
            self.tx_errors.append("Amount must be greater than zero.")

        if self.fee < 0:
            self.tx_errors.append("Fee cannot be negative.")

        if self.tx_errors:
            return
        try:
            transaction = Transaction.create_by_receiver_username(
                sender=UserService.logged_in_user,
                receiver_username=self.to,
                amount=self.amount,
                fee=self.fee,
            )
            transaction.validate(raise_exception=True, include_reserved_balance=True)
        except InvalidTransactionException as e:
            self.tx_errors.append(str(e))
            self.mutate_reactive(TransactionCreateScreen.tx_errors)
            return
        except InsufficientBalanceException as e:
            self.tx_errors.append(str(e))
            self.mutate_reactive(TransactionCreateScreen.tx_errors)
            return

        # Clear all fields
        self.to = ""
        self.amount = Decimal("0.0")
        self.fee = Decimal("0.0")

        self.tx_errors = []

        from blockchain import Pool
        Pool.get_instance().add_transaction(transaction)

        self.app.switch_screen(AlertScreen(UIAlert(
            title="Transaction successful",
            message="The transaction has been created successfully and is added to the Pool.",
            alert_type=AlertType.SUCCESS
        )))

        self.mutate_reactive(TransactionCreateScreen.tx_errors)

