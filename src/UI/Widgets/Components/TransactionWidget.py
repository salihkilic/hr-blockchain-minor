from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem

from Repositories.Transaction import MockTransactionRepository


class BlockInfoWidget(Widget):
    CSS = """
        """

    # const

    def __init__(self, ):
        self.TransactionRepository = MockTransactionRepository()
        super().__init__()

    def compose(self) -> ComposeResult:
        visible_block = 23

        txs = self.TransactionRepository.find_by_block_id(visible_block)
        txs_widgets = map(lambda tx: ListItem(Label(f"{tx.tx_type.name} | Transaction {tx.tx_id}: From {tx.sender} to {tx.receiver} - Amount: {tx.amount} GCN"), classes="transaction"), txs)

        yield Vertical(
            Label(f"Block #{visible_block}"),
            Rule(line_style="heavy"),
            Horizontal(
                Button("Previous Block", id="prev_block"),
                Button("Next Block", id="next_block", disabled=True),
                classes="button-row"
            ),
            ListView(
                *txs_widgets,
                classes="transactions_scroll"
            )
        )