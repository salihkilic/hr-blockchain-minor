from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label


class UserDetails(Widget):

    def compose(self) -> ComposeResult:
        yield Label("User details", classes="column-header")

