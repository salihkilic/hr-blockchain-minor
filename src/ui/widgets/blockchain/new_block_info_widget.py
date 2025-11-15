from textual import log, events
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Ledger, Pool
from models import Transaction
from models.block import BlockStatus
from .transaction_listing_widget import TransactionListingWidget


class NewBlockInfoWidget(Widget):
    DEFAULT_CSS = """
            .button_col {
                height: auto;
            }
            .button_row {
                height: auto;
                padding: 1 0;
            }
            .button {
                width: 50%;
            }
            .block__title {
                padding: 1 2;
                background: lightskyblue 20%;
                width: 100%;
                text-align: center;
                text-style: bold;
            }
            .block__status {
                padding: 1 1;
                margin: 1 0 0 0;
                width: 100%;
                text-align: center;
                text-style: bold;
            }
            .block__status--accepted {
                background: lightgreen 40%;
            }
            .block__status--rejected {
                background: lightcoral 40%;
            }
            .block__status--pending {
                background: lightyellow 40%;
            }
            .block__title--genesis {
                background: ansi_blue 20%;
            }
        """

    marked_transactions: list[Transaction] = reactive(Pool.get_instance().get_transactions_marked_for_block,
                                                      recompose=True)
    valid_for_mining: bool = reactive(False, recompose=True)

    def __init__(self, ):
        super().__init__()

    def on_mount(self) -> None:
        Pool.subscribe(self.update_marked_transactions)

    def update_marked_transactions(self, param):
        self.marked_transactions = Pool.get_instance().get_transactions_marked_for_block()
        self.mutate_reactive(NewBlockInfoWidget.marked_transactions)

    def compose(self) -> ComposeResult:

        txs = self.marked_transactions
        txs.sort(key=lambda tx: tx.timestamp)

        yield Vertical(
            Label(f"New block", classes="block__title"),
            Vertical(
                Horizontal(
                    Button("Mine block", classes="button", id="mine_block"),
                    Button("Move all blocks back to the pool", id="move_all_blocks", classes="button"),
                    classes="button_col"
                ),
                classes="button_row"
            ),
            Label(f"Transactions ({len(self.marked_transactions)}):", classes="block__title"),
            VerticalScroll(
                *list(map(lambda tx: TransactionListingWidget(tx), txs)),
                classes="transactions_scroll"
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "mine_block":
            from ui.screens.blockchain import BlockMiningScreen
            self.app.push_screen(BlockMiningScreen())
        if event.button.id == "move_all_blocks":
            Pool.get_instance().unmark_all_transaction()
