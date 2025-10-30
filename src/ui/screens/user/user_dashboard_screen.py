from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder

class UserDashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("User dashboard screen")
        yield Footer()

    def on_mount(self) -> None:
        if True:
             self.app.push_screen("login_screen")
