from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, ListView, ListItem


class LiveTransactionPool(Widget):

    def compose(self) -> ComposeResult:

        yield Label("Live transaction pool", classes="column-header")
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )

    def _demo_generate_random_transactions(self):
        amount = 15
        transactions = []
        # format amount from hash to
        for i in range(amount):
            random_number = "0x" + "".join(["%x" % __import__("random").randint(0, 15) for _ in range(64)])
            transactions.append(f"tx_{random_number}: {i*10} GC")