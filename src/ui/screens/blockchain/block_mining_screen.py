from decimal import Decimal

from textual import events
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal, Container
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Footer, Placeholder, Static, Input, Button, ListItem, Label, ListView, Rule, \
    LoadingIndicator

from models import Transaction
from models.dto import UIAlert
from models.enum import AlertType
from ui.screens.utils.alert_screen import AlertScreen


class BlockMiningScreen(Screen):

    DEFAULT_CSS = """
        Button {
            margin: 0 2;
        }
        BlockMiningScreen{
            margin: 2;
            padding: 1;
        }
        Input {
            margin: 1 2;
        }
        Label {
            margin: 0 2;
        }
        Container {
            height: 20%;
            width: 100%;
        }
    """

    def __init__(self):
        super().__init__()
        self.timer = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Mining block nr: 25"),
            Label("Mining will take approximately 10 to 20 seconds."),
            Container(
                LoadingIndicator(),
            ),
            Horizontal(
                Button("Cancel mining", id="close"),
                classes="button-row",
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        self.timer: Timer = self.set_timer(3, lambda: self.app.call_later(self._fake_mine))

    def _fake_mine(self) -> None:
        self.app.switch_screen(AlertScreen(UIAlert(
            title="Mining successful",
            message="Block has been mined successfully.",
            alert_type=AlertType.SUCCESS
        )))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":

            if hasattr(self, "_timer"):
                self.timer.stop()

            self.app.switch_screen(AlertScreen(UIAlert(
                title="Mining cancelled",
                message="Block mining has been cancelled by the user.",
                alert_type=AlertType.WARNING
            )))