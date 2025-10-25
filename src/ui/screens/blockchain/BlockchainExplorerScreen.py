from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Label

from ui.widgets.blockchain import BlockInfoWidget, TransactionPoolWidget


class BlockchainExplorerScreen(Screen):
    def compose(self) -> ComposeResult:
        column_user_info = Vertical(
            Placeholder("User Info"),
            classes="column"
        )
        column_user_info.border_title = "User Information"

        column_block_info = Vertical(
            BlockInfoWidget(),
            classes="column"
        )
        column_block_info.border_title = "Block information"


        column_transaction_pool = Vertical(
            TransactionPoolWidget(),
            classes="column"
        )
        column_transaction_pool.border_title = "Transaction Pool"

        yield Horizontal(
            column_user_info,
            column_block_info,
            column_transaction_pool,
            classes="container"
        )
        yield Footer()
