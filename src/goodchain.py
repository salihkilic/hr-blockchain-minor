from decimal import Decimal

from textual.app import App

from blockchain import Pool
from blockchain.ledger import Ledger
from models import User, Transaction
from repositories.user import UserRepository
from services import FileSystemService
from ui.screens.blockchain import BlockchainExplorerScreen, TransactionDetailScreen, TransactionCreateScreen, \
    BlockMineScreen, BlockMiningScreen
from ui.screens.user import UserDashboardScreen, UserLoginScreen, UserRegisterScreen

class BlockchainApp(App):

    BINDINGS = [
        ("b", "switch_mode('blockchain_explorer')", "Blockchain Explorer"),
        ("u", "switch_mode('user_dashboard')", "User Dashboard")
    ]
    MODES = {
        "blockchain_explorer": BlockchainExplorerScreen,
        "user_dashboard": UserDashboardScreen,
    }
    SCREENS = {
        "login_screen": UserLoginScreen,
        "register_screen": UserRegisterScreen,
        "transaction_detail_screen": TransactionDetailScreen,
        "transaction_create_screen": TransactionCreateScreen,
        "block_mine_screen": BlockMineScreen,
        "block_mining_screen": BlockMiningScreen
    }

    def on_mount(self) -> None:
        filesystem_service = FileSystemService()
        filesystem_service.initialize_data_files()

        user_repository = UserRepository()
        user_repository.setup_database_structure()

        Pool.create_instance()
        Ledger.create_instance()

        self.switch_mode("blockchain_explorer")


if __name__ == "__main__":
    app = BlockchainApp()
    app.run()
