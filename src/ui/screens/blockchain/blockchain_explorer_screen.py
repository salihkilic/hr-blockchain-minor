from textual import events, log
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Label

from ui.widgets.blockchain import BlockInfoWidget, TransactionPoolWidget, UserInfoWidget


class BlockchainExplorerScreen(Screen):

    DEFAULT_CSS = """
        .column{
            margin: 2;
            padding: 1;
        }

    """

    def compose(self) -> ComposeResult:
        column_user_info = Vertical(
            UserInfoWidget(),
            classes="column"
        )
        column_user_info.border_title = "User Information"
        column_user_info.styles.border = ("double", "blueviolet")

        column_block_info = Vertical(
            BlockInfoWidget(),
            classes="column"
        )
        column_block_info.border_title = "Block information"
        column_block_info.styles.border = ("double", "lightskyblue")


        column_transaction_pool = Vertical(
            TransactionPoolWidget(),
            classes="column"
        )
        column_transaction_pool.border_title = "Transaction Pool"
        column_transaction_pool.styles.border = ("double", "orange")

        yield Horizontal(
            column_user_info,
            column_block_info,
            column_transaction_pool,
            classes="container"
        )
        yield Footer()

    def _on_screen_resume(self) -> None:
        self.refresh()
