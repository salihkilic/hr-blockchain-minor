import time
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.screen import Screen
from textual.widgets import Footer, Label, LoadingIndicator
from models.dto import UIAlert
from models.enum import AlertType
from ui.screens.utils.alert_screen import AlertScreen

class TransactionRemovalScreen(Screen):

    DEFAULT_CSS = """
        Button {
            margin: 0 2;
        }
        TransactionRemovalScreen{
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
            height: 10;
            width: 100%;
        }
        .title{
            margin: 2;
            padding: 1;
            background: blue;
            width: 100%;
            text-align: center;
        }

    """

    def __init__(self):
        super().__init__()
        self.timer = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Removing your invalid transactions", classes="title"),
            Container(
                LoadingIndicator(),
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        self._validate_ledger()

    @work(exclusive=True, thread=True)
    def _validate_ledger(self):
        try:
            # TODO Validate ledger
            time.sleep(2)
        except Exception as e:
            self.app.call_from_thread(
                self.app.switch_screen,
                AlertScreen(UIAlert(
                    title="Ledger validation failed",
                    message=f"The ledger validation failed due to an error: {e}",
                    alert_type=AlertType.DANGER,
                    dismissed_automatically=False
                ), terminate_after_dismiss=True)
            )
            return

            # success case
        self.app.call_from_thread(self.show_ledger_valid)


    def show_ledger_valid(self):
        self.app.switch_screen(AlertScreen(UIAlert(
            title="Automatically removed invalid transactions",
            message="The following transactions were found to be invalid and have been removed from your transaction pool:",
            alert_type=AlertType.WARNING,
            dismissed_automatically=False
        )))