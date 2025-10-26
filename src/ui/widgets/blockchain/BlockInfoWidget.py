from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from repositories.transaction import MockTransactionRepository
from .TransactionListingWidget import TransactionListingWidget


class BlockInfoWidget(Widget):
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
            .block__title {
                padding: 1 2;
                background: lightskyblue 20%;
                width: 100%;
                text-align: center;
                text-style: bold;
            }
        """

    def __init__(self, ):
        self.TransactionRepository = MockTransactionRepository()
        super().__init__()

    def compose(self) -> ComposeResult:
        visible_block = 23

        txs = self.TransactionRepository.find_by_block_id(visible_block)
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), txs))

        yield Vertical(
            Label(f"Block nr: {visible_block}", classes="block__title"),
            Vertical(
                Horizontal(
                    Button("Previous", classes="button"),
                    Button("Next", classes="button", disabled=True),
                    classes="button_col"
                ),
                Horizontal(
                    Button("Mine block", classes="button", disabled=True),
                    classes="button_col"
                ),
                classes="button_row"
            ),
            VerticalScroll(
                *txs_widgets,
                classes="transactions_scroll"
            ),
        )

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
