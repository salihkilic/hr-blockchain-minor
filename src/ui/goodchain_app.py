from textual.app import App

from services import StartupService


class GoodchainApp(App):

    from ui.screens.blockchain import BlockchainExplorerScreen, TransactionDetailScreen, TransactionCreateScreen, \
        BlockMiningScreen
    from ui.screens.user import UserLoginScreen, UserRegisterScreen

    MODES = {
        "blockchain_explorer": BlockchainExplorerScreen,
    }
    SCREENS = {
        "login_screen": UserLoginScreen,
        "register_screen": UserRegisterScreen,
        "transaction_detail_screen": TransactionDetailScreen,
        "transaction_create_screen": TransactionCreateScreen,
        "block_mining_screen": BlockMiningScreen,
    }

    def on_mount(self) -> None:
        self.switch_mode("blockchain_explorer")