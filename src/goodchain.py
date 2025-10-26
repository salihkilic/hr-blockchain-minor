from textual.app import App

from repositories.user import UserRepository
from ui.screens.blockchain import BlockchainExplorerScreen, TransactionDetailScreen
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
    }

    def on_mount(self) -> None:
        user_repository = UserRepository()
        user_repository.setup_database_structure()

        self.switch_mode("blockchain_explorer")


if __name__ == "__main__":
    app = BlockchainApp()
    app.run()
