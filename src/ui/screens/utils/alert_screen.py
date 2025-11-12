import time
from decimal import Decimal

from textual import events
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button, ListItem, Label, ListView, Rule

from models import Transaction
from models.dto import UIAlert
from models.enum import AlertType


class AlertScreen(Screen):
    DEFAULT_CSS = """
        AlertScreen{
            margin: 2;
            padding: 1;
        }
        Label {
            margin: 1 2;
        }
        Vertical {
            margin: 2;
            padding: 1;
        }
    """

    def __init__(self, alert: UIAlert):
        super().__init__()
        self.alert = alert

    def compose(self) -> ComposeResult:
        vertical = Vertical(
            Label(self.alert.message, classes="message")
        )
        vertical.border_title = self.alert.title

        if self.alert.alert_type == AlertType.SUCCESS:
            vertical.styles.border = ("double", "green")
        if self.alert.alert_type == AlertType.WARNING:
            vertical.styles.border = ("double", "goldenrod")
        if self.alert.alert_type == AlertType.INFO:
            vertical.styles.border = ("double", "blue")
        if self.alert.alert_type == AlertType.DANGER:
            vertical.styles.border = ("double", "red")

        if not self.alert.dismissed_automatically:
            yield Button("Close", id="close")

        yield vertical
        yield Footer()

    async def on_mount(self) -> None:
        if self.alert.dismissed_automatically:
            self.set_timer(3, lambda: self.app.call_later(self.app.pop_screen))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()
