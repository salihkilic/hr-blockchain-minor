import asyncio
from decimal import Decimal

from textual import events, log, work
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal, Container
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Footer, Placeholder, Static, Input, Button, ListItem, Label, ListView, Rule, \
    LoadingIndicator
from textual.worker import Worker

from blockchain import Ledger
from exceptions.mining import InvalidBlockException
from exceptions.transaction import InvalidTransactionException
from models import Transaction, Block
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
        log("BlockMiningScreen mounted, starting mining process...")
        self._mine_transactions_marked_for_block()

    def _mine_transactions_marked_for_block(self) -> None:
        self._start_block_mine()


    @work(exclusive=True, thread=True)
    def _start_block_mine(self):
        log("Starting block mining...")
        try:
            Ledger.mine_new_block()
        except InvalidTransactionException as e:
            self.app.call_from_thread(
                self.app.switch_screen,
                AlertScreen(UIAlert(
                    title="Mining failed",
                    message=f"Block mining failed due to invalid transaction: {e}",
                    alert_type=AlertType.DANGER
                ))
            )
            return

        except InvalidBlockException as e:
            self.app.call_from_thread(
                self.app.switch_screen,
                AlertScreen(UIAlert(
                    title="Mining failed",
                    message=f"Block mining failed due to invalid block: {e}",
                    alert_type=AlertType.DANGER
                ))
            )
            return

            # success case
        self.app.call_from_thread(self.show_mining_success)


    def show_mining_success(self):
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