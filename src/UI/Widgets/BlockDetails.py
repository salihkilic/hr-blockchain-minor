from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label


class BlockDetails(Widget):

    def compose(self) -> ComposeResult:

        # Create hex random value
        random_number = "0x" + "".join(["%x" % __import__("random").randint(0, 15) for _ in range(64)])

        yield Label("Block details", classes="column-header")
        yield Label(random_number)

