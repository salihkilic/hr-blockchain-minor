from faker import Faker
from textual import log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from models import User
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
        """

    logged_in_user: User | None = reactive(None, recompose=True)

    def __init__(self, ):
        super().__init__()
        self.logged_in_user = UserService.logged_in_user

    def on_mount(self):
        UserService.subscribe(self.update_user)

    def update_user(self, user: User | None):
        log(f"UserInfoWidget received user update: {user}")
        self.logged_in_user = user

    def compose(self) -> ComposeResult:
        log("Composing UserInfoWidget with logged_in_user: {}".format(self.logged_in_user))

        if self.logged_in_user is None:
            yield Vertical(
                Label(f"Log in or register to use this module", classes="block__title block__title--inverted"),
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

        yield Vertical(
            Label(f"User: {self.logged_in_user.username}", classes="block__title"),
            Vertical(
                Horizontal(
                    Label("Balance: 79.0", classes="col__label"),
                    Label("Reserved: 10.0", classes="col__label"),
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
