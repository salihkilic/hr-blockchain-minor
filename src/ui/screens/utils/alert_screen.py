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

        yield vertical
        yield Footer()

    async def on_mount(self) -> None:
        self.set_timer(3, lambda: self.app.call_later(self.app.pop_screen))
