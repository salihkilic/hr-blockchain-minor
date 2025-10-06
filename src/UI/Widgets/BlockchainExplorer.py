from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class BlockchainExplorer(Widget):

    def __init__(self, title: str = "Blockchain Explorer"):
        super().__init__()
        self.title = title

    def compose(self) -> ComposeResult:
        yield Label("Your TEXT here!")