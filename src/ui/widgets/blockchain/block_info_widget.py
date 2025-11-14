from textual import log
from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from blockchain import Ledger
from models.block import BlockStatus
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

    visible_block_number: int = reactive(0, recompose=True)

    def __init__(self, ):
        super().__init__()
        pending_block = Ledger.get_instance().get_pending_block()
        log(f"Initializing BlockInfoWidget, pending block: {pending_block}")
        if pending_block is not None:
            self.visible_block_number = pending_block.number
        else:
            latest_block = Ledger.get_instance().get_latest_block()
            if latest_block is not None:
                self.visible_block_number = latest_block.number


    def compose(self) -> ComposeResult:
        log(f"Composing BlockInfoWidget for block number: {self.visible_block_number}")
        visible_block = Ledger.get_instance().get_block_by_number(number=self.visible_block_number, include_pending=True)

        if visible_block is None:
            yield Vertical(
                Label("No blocks in the ledger.", classes="block__title"),
            )
            return

        is_last_block = visible_block == Ledger.get_instance().get_latest_block(include_pending=True)
        is_first_block = visible_block is not None and visible_block.number == 0

        txs = visible_block.transactions
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), txs))

        children = []

        children.append(
            Label(f"Block nr: {visible_block.number}", classes="block__title") if visible_block.number > 0 else Label(
                f"Genesis Block", classes="block__title block__title--genesis"),
        )

        if visible_block.status == BlockStatus.PENDING:
            children.append(
                Label("This block is pending validation.", classes="block__status block__status--pending")
            ),
            valids = visible_block.validation_valid_len()
            invalids = visible_block.validation_invalid_len()
            children.append(
                Label(f"Validations: {valids} valid, {invalids} invalid.", classes="block__status block__status--pending")
            )

        if visible_block.number > 0 and visible_block.status != BlockStatus.PENDING:
            classes = "block__status"
            if visible_block.status == BlockStatus.ACCEPTED:
                classes += " block__status--accepted"
            if visible_block.status == BlockStatus.REJECTED:
                classes += " block__status--rejected"
            if visible_block.status == BlockStatus.PENDING:
                classes += " block__status--pending"
            children.append(
                Label(f"Block status: {visible_block.status.value.capitalize()}", classes=classes)
            )

        children.append(
            Vertical(
                Horizontal(
                    Button("Previous", id="prev_block", classes="button", disabled=is_first_block),
                    Button("Next", id="next_block", classes="button", disabled=is_last_block),
                    classes="button_col"
                ),
                classes="button_row"
            )
        )

        children.append(
            VerticalScroll(
                *txs_widgets,
                classes="transactions_scroll"
            )
        )

        yield Vertical(
            *children
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "prev_block":
            log(f"Current visible block number: {self.visible_block_number}, trying to go to previous block")
            if self.visible_block_number > 0:
                log(f"Going to previous block number: {self.visible_block_number - 1}")
                self.visible_block_number -= 1
                self.recompose()
            else:
                log(f"Already at the first block, cannot go back further.")
        if event.button.id == "next_block":
            latest_block = Ledger.get_instance().get_latest_block(include_pending=True)
            if latest_block and self.visible_block_number < latest_block.number:
                self.visible_block_number += 1
