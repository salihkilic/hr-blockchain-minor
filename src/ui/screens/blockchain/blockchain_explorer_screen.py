from textual import events, log
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Label

from blockchain import Ledger
from ui.widgets.blockchain import BlockInfoWidget, TransactionPoolWidget, UserInfoWidget, NewBlockInfoWidget


class BlockchainExplorerScreen(Screen):

    DEFAULT_CSS = """
        .column{
            margin: 2;
            padding: 1;
        }

    """

    block_pending_mining: bool = reactive(False, recompose=True)

    def on_mount(self):
        from blockchain import Pool
        Pool.subscribe(self.update_block_pending_mining_status)

    def update_block_pending_mining_status(self, param):
        from blockchain import Pool
        transactions_marked = Pool.get_instance().get_transactions_marked_for_block()
        log(f"Updating block_pending_mining status: {len(transactions_marked)}")
        self.block_pending_mining = len(transactions_marked) > 0

    def compose(self) -> ComposeResult:
        column_user_info = Vertical(
            UserInfoWidget(),
            classes="column"
        )
        column_user_info.border_title = "User Information"
        column_user_info.styles.border = ("double", "blueviolet")

        if not self.block_pending_mining:
            column_block_info = Vertical(
                BlockInfoWidget(),
                classes="column"
            )
            column_block_info.border_title = "Block information"
            column_block_info.styles.border = ("double", "lightskyblue")
        else:
            column_block_info = Vertical(
                NewBlockInfoWidget(),
                classes="column"
            )
            column_block_info.border_title = "New block"
            column_block_info.styles.border = ("double", "greenyellow")


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
