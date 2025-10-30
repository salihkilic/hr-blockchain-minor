from decimal import Decimal

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button, ListItem, Label, ListView, Rule

from models import Transaction


class TransactionCreateScreen(Screen):

    DEFAULT_CSS = """
        Button {
            margin: 2;
        }
        TransactionCreateScreen{
            margin: 2;
            padding: 1;
        }
        Input {
            margin: 1 2;
        }
        Label {
            margin: 0 2;
        }
    """

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Create a new transaction"),
            Input(placeholder="To"),
            Input(placeholder="Amount"),
            Input(placeholder="Fee"),
            Rule(line_style="double"),
            Input(placeholder="Authorization key", password=True),
            Horizontal(
                Button("Create", id="register"),
                Button("Cancel", id="close"),
                classes="button-row",
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()