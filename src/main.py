from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class UserDashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("User Dashboard")
        yield Footer()

class BlockchainExplorer(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Blockchain Explorer")
        yield Footer()


class BlockchainApp(App):
    BINDINGS = [
        ("b", "switch_mode('blockchain_explorer')", "Blockchain Explorer"),
        ("u", "switch_mode('user_dashboard')", "User Dashboard"),
    ]
    MODES = {
        "blockchain_explorer": BlockchainExplorer,
        "user_dashboard": UserDashboardScreen,
    }

    def on_mount(self) -> None:
        self.switch_mode("blockchain_explorer")


if __name__ == "__main__":
    app = BlockchainApp()
    app.run()