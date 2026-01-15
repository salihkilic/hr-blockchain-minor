import asyncio
import logging

from textual.app import App

from events import BlockAddedFromNetworkEvent, TransactionAddedFromNetworkEvent, ValidationAddedFromNetworkEvent, \
    LoginValidationCompletedEvent, GenesisBlockAddedFromNetworkEvent
from services import StartupService, NetworkingService, CatchupService
from services.user_service import UserService
from ui.screens.startup import BlockValidationScreen


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

        catchup_service = CatchupService()
        catchup_service.request_block_catchup(
            after_number=latest_block.number if latest_block and latest_block.number != 0 else -1
        )
        catchup_service.request_pool_catchup()
        catchup_service.request_validation_catchup()

        catchup_service.volunteer_block_catchup()
        catchup_service.volunteer_pool_catchup()
        catchup_service.volunteer_validation_catchup()

        BlockAddedFromNetworkEvent.subscribe(lambda _: self.notify(
            title='Network event',
            message='A block was received from the network and added to the ledger.'
        ))

        GenesisBlockAddedFromNetworkEvent.subscribe(lambda _: self.notify(
            title='Network event',
            message='The genesis block was received from the network and added to the ledger.',
            severity="warning"
        ))

        TransactionAddedFromNetworkEvent.subscribe(lambda _: self.notify(
            title='Network event',
            message='A transaction was received from the network and added to the pool.'
        ))

        ValidationAddedFromNetworkEvent.subscribe(lambda _: self.notify(
            title='Network event',
            message='A validation was received from the network and added to the ledger.'
        ))

        BlockAddedFromNetworkEvent.subscribe(lambda _: self.validate_new_block())

    def validate_new_block(self) -> None:
        # Check if there is pending block that this user has not validated yet
        from blockchain import Ledger

        user = UserService.logged_in_user
        if user is None:
            return

        pending_block = Ledger.get_instance().get_pending_block()
        if pending_block is None:
            return

        validators = pending_block.validators

        if user.public_key in validators:
            return  # User has already validated this block

        logging.debug("Starting new block validation")

        logging.debug(f"Current screen count {len(self.screen_stack)}")

        if len(self.screen_stack) > 1:
            self.pop_screen()

        self.push_screen(BlockValidationScreen(close_after_validation=True))



    def on_shutdown(self) -> None:
        NetworkingService.get_instance().stop()
        self._network_task.cancel()