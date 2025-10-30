from faker import Faker
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from models import User
from repositories.transaction import MockTransactionRepository
from .transaction_listing_widget import TransactionListingWidget


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
        """

    def __init__(self, ):
        self.TransactionRepository = MockTransactionRepository()
        super().__init__()

    def compose(self) -> ComposeResult:

        logged_in_user = User(
            username=Faker().user_name(),
            password_hash=Faker().sha256(),
            public_key=Faker().sha256(),
            private_key=Faker().sha256(),
            salt="static_salt",
            key_type="RSA"
        )

        txs = self.TransactionRepository.find_by_user(logged_in_user)
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), txs))

        yield Vertical(
            Label(f"User: {logged_in_user.username}", classes="block__title"),
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

        #
        # yield Vertical(
        #     Label(f"State mined"),
        #     Rule(line_style="heavy"),
        #     Label(f"Block #{visible_block}"),
        #     Rule(line_style="heavy"),
        #     Horizontal(
        #         Button("Previous Block", id="prev_block"),
        #         Button("Next Block", id="next_block", disabled=True),
        #         classes="button-row"
        #     ),
        #     *txs_widgets,
        #     Rule(line_style="heavy"),
        # )
