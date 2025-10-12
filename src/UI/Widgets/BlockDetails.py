from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label


class BlockDetails(Widget):

    def compose(self) -> ComposeResult:
        yield Label("Block details", classes="column-header")

