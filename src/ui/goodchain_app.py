import asyncio

from textual.app import App

from services import StartupService, NetworkingService


class GoodchainApp(App):

    _network_task: asyncio.Task[None]

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

        self._network_task = asyncio.create_task(
            NetworkingService.get_instance().listen()
        )

    def on_shutdown(self) -> None:
        NetworkingService.get_instance().stop()
        self._network_task.cancel()