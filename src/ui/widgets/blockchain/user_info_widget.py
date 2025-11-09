from decimal import Decimal

from faker import Faker
from textual import log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Pool
from models import User, Wallet
from models.dto import UIAlert
from models.enum import AlertType
from services.user_service import UserService
from .transaction_listing_widget import TransactionListingWidget
from ...screens.utils import AlertScreen


class UserInfoWidget(Widget):
    DEFAULT_CSS = """
            .col {
                height: auto;
            }
            .row {
                height: auto;
                padding: 1 0;
            }
            .col__label,
            .button {
                width: 50%;
            }
            .block__title {
                padding: 1 2;
                background: blueviolet 20%;
                width: 100%;
                text-style: bold;
            }
            .block__title--inverted {
                background: rgba(0, 0, 0, 0.0);
                color: blueviolet;
            }
            .col__label--warning {
                color: orange;
            }
        """

    logged_in_user: User | None = reactive(None, recompose=True)
    balance: Decimal = reactive(Decimal("0.00"), recompose=True)
    reserved_balance: Decimal = reactive(Decimal("0.00"), recompose=True)

    def __init__(self, ):
        super().__init__()
        self.logged_in_user = UserService.logged_in_user
        self.update_balance(None)

    def on_mount(self):
        UserService.subscribe(self.update_user)
        Pool.subscribe(self.update_balance)

    def update_user(self, user: User | None):
        log(f"UserInfoWidget received user update: {user.username if user else 'None'}")
        self.logged_in_user = user
        self.update_balance(None)

    def update_balance(self, data):
        log("UserInfoWidget received pool update")
        if self.logged_in_user is None:
            self.balance = Decimal("0.00")
            self.reserved_balance = Decimal("0.00")
            return
        wallet = Wallet.from_user(self.logged_in_user)
        self.balance = wallet.balance
        self.reserved_balance = wallet.reserved_balance


    def compose(self) -> ComposeResult:
        log("Composing UserInfoWidget with logged_in_user: {}".format(self.logged_in_user))

        if self.logged_in_user is None:
            yield Vertical(
                Label(f"Log in or register to use this module", classes=("block__title block__title--inverted")),
                Vertical(
                    Horizontal(
                        Button("Login", id="login", classes="button"),
                        classes="col"
                    ),
                    classes="row"
                ),
            )
            return

        txs = []
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), txs))

        balance = self.balance.quantize(Decimal("0.00"))
        reserved_balance = self.reserved_balance.quantize(Decimal("0.00")).__abs__()
        spendable_balance = (self.balance + self.reserved_balance).quantize(Decimal("0.00"))

        yield Vertical(
            Label(f"User: {self.logged_in_user.username}", classes="block__title"),
            Label(f"{self.logged_in_user.address}", classes="block__title"),
            Vertical(
                Horizontal(
                    Label(f"Balance: {balance}", classes="col__label"),
                    Label(f"Reserved: {reserved_balance}", classes="col__label " + ("col__label--warning" if reserved_balance > 0 else "")),
                    classes="col"
                ),
                Horizontal(
                    Label(f"Spendable balance: {spendable_balance}", classes="col__label"),
                    classes="col"
                ),
                classes="row"
            ),
            Vertical(
                Horizontal(
                    Button("Show public key", classes="button"),
                    Button("Show private key", classes="button"),
                    classes="col"
                ),
                Horizontal(
                    Button("Logout", classes="button"),
                    Button("Create transaction", classes="button", id="create_transaction"),
                    classes="col"
                ),
                classes="row"
            ),
            VerticalScroll(
                *txs_widgets,
                classes="transactions_scroll"
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_transaction":
            self.app.push_screen("transaction_create_screen")
        if event.button.label == "Logout":
            user_service = UserService()
            user_service.logout()
        if event.button.id == "login":
            self.app.push_screen("login_screen")
        if event.button.label == "Show public key":
            if self.logged_in_user is not None:
                self.app.push_screen(AlertScreen(UIAlert(
                    title="Public Key",
                    message=self.logged_in_user.public_key,
                    dismissed_automatically=False,
                    alert_type=AlertType.INFO
                )))
        if event.button.label == "Show private key":
            if self.logged_in_user is not None:
                self.app.push_screen(AlertScreen(UIAlert(
                    title="Private Key",
                    message=self.logged_in_user.private_key,
                    dismissed_automatically=False,
                    alert_type=AlertType.DANGER
                )))
