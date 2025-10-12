from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Placeholder, ListItem, ListView, Label, Static

from UI.Widgets.BlockDetails import BlockDetails
from UI.Widgets.LiveTransactionPool import LiveTransactionPool
from UI.Widgets.UserDetails import UserDetails


class GoodchainApp(App):
    CSS_PATH = "GoodchainApp.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Horizontal(
            Vertical(
                UserDetails(),
                classes="column",
            ),
            Vertical(
                BlockDetails(),
                classes="column",
            ),
            Vertical(
                LiveTransactionPool(),
                classes="column",
            ),
            classes="container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Goodchain"
