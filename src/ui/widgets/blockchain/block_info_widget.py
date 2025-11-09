from textual import log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Ledger
from .transaction_listing_widget import TransactionListingWidget


class BlockInfoWidget(Widget):
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
                width: 100%;
                text-align: center;
                text-style: bold;
            }
            .block__title--genesis {
                background: lightgreen 20%;
            }
        """

    visible_block_number: int = reactive(0, recompose=True)

    def __init__(self, ):
        super().__init__()
        latest_block = Ledger.get_instance().get_latest_block()
        self.visible_block_number = latest_block.number if latest_block is not None else 0

    def compose(self) -> ComposeResult:
        log(f"Composing BlockInfoWidget for block number: {self.visible_block_number}")
        visible_block = Ledger.get_instance().get_block_by_number(self.visible_block_number)

        if visible_block is None:
            yield Vertical(
                Label("No blocks in the ledger.", classes="block__title"),
            )
            return

        is_last_block = visible_block == Ledger.get_instance().get_latest_block()
        is_first_block = visible_block is not None and visible_block.number == 0

        txs = visible_block.transactions
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), txs))

        yield Vertical(
            Label(f"Block nr: {visible_block.number}", classes="block__title") if visible_block.number > 0 else Label(f"Genesis Block", classes="block__title block__title--genesis"),
            # TODO Implement status
            # Label(f"Block status: TODO", classes="block__status"),
            Vertical(
                Horizontal(
                    Button("Previous", id="prev_block", classes="button", disabled=is_first_block),
                    Button("Next", id="next_block", classes="button", disabled=is_last_block),
                    classes="button_col"
                ),
                Horizontal(
                    Button("Mine block", classes="button", id="mine_block"),
                    classes="button_col"
                ),
                classes="button_row"
            ),
            VerticalScroll(
                *txs_widgets,
                classes="transactions_scroll"
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "mine_block":
            self.app.push_screen("block_mine_screen")
        if event.button.id == "prev_block":
            log(f"Current visible block number: {self.visible_block_number}, trying to go to previous block")
            if self.visible_block_number > 0:
                log(f"Going to previous block number: {self.visible_block_number - 1}")
                self.visible_block_number -= 1
                self.recompose()
            else:
                log(f"Already at the first block, cannot go back further.")
        if event.button.id == "next_block":
            latest_block = Ledger.get_instance().get_latest_block()
            if latest_block and self.visible_block_number < latest_block.number:
                self.visible_block_number += 1
