from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem, Collapsible, Markdown

from repositories.transaction import MockTransactionRepository
from .transaction_listing_widget import TransactionListingWidget


class TransactionPoolWidget(Widget):
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
        """

    def __init__(self, ):
        self.TransactionRepository = MockTransactionRepository()
        super().__init__()

    def compose(self) -> ComposeResult:

        txs = self.TransactionRepository.find_in_transactions_pool()
        txs_widgets = list(map(lambda tx: TransactionListingWidget(tx), txs))

        yield Vertical(
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
