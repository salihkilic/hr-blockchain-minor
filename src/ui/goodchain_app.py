import asyncio

from textual.app import App

from events import BlockAddedFromNetworkEvent, TransactionAddedFromNetworkEvent
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

        from blockchain import Ledger
        latest_block = Ledger.get_instance().get_latest_block()
        NetworkingService.get_instance().request_next_block(
            after_number=latest_block.number if latest_block else -1,
        )

        # NetworkingService.get_instance().request_pool_snapshot()

        BlockAddedFromNetworkEvent.subscribe(lambda _: self.notify(
            title='Network event',
            message='A block was received from the network and added to the ledger.'
        ))

        TransactionAddedFromNetworkEvent.subscribe(lambda _: self.notify(
            title='Network event',
            message='A transaction was received from the network and added to the pool.'
        ))

    def on_shutdown(self) -> None:
        NetworkingService.get_instance().stop()
        self._network_task.cancel()