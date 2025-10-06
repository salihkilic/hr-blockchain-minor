from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class BlockchainExplorerScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Blockchain Explorer")
        yield Footer()


class UserDashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("User Dashboard")
        yield Footer()


class DebugScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Debug screen")
        yield Footer()


class ModesApp(App):
    BINDINGS = [
        ("b", "switch_mode('blockchain_explorer')", "Blockchain Explorer"),
        ("u", "switch_mode('user_dashboard')", "User Dashboard"),
        ("d", "switch_mode('debug_screen')", "Debug Screen"),
    ]
    MODES = {
        "blockchain_explorer": BlockchainExplorerScreen,
        "user_dashboard": UserDashboardScreen,
        "debug_screen": DebugScreen,
    }

    def on_mount(self) -> None:
        self.switch_mode("blockchain_explorer")


if __name__ == "__main__":
    app = ModesApp()
    app.run()