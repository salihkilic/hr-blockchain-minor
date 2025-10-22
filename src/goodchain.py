from textual.app import App
from Database.sqlite_client import Database  # Initialize DB on app startup
from UI.Screens.Blockchain import BlockchainExplorerScreen
from UI.Screens.User import UserDashboardScreen, UserLoginScreen, UserRegisterScreen





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
        "register_screen": UserRegisterScreen
    }

    def on_mount(self) -> None:
        # Initialize the user database once at app startup
        self.db = Database()
        self.db.connect()
        self.db.init_schema()
        # Switch to default mode
        self.switch_mode("blockchain_explorer")


if __name__ == "__main__":
    app = BlockchainApp()
    app.run()
