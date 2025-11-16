import time
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.screen import Screen
from textual.widgets import Footer, Label, LoadingIndicator

from exceptions.mining import InvalidBlockException
from exceptions.transaction import InvalidTransactionException
from models.dto import UIAlert
from models.enum import AlertType
from ui.screens.utils.alert_screen import AlertScreen


class LedgerValidationScreen(Screen):
    DEFAULT_CSS = """
        Button {
            margin: 0 2;
        }
        LedgerValidationScreen{
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

    def __init__(self, close_after: bool = False):
        super().__init__()
        self.close_after = close_after

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Validating chain", classes="title"),
            Container(
                LoadingIndicator(),
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        self._validate_ledger()

    @work(exclusive=True, thread=True)
    def _validate_ledger(self):
        from blockchain import Ledger
        try:
            (valid, errors) = Ledger.get_instance().validate_chain()
        except InvalidTransactionException as e:
            valid = False
            errors = [str(e)]
        except InvalidBlockException as e:
            valid = False
            errors = [str(e)]

        if not valid:
            self.app.call_from_thread(
                self.app.switch_screen,
                AlertScreen(UIAlert(
                    title="Chain validation failed",
                    message=f"The chain validation failed due to {'an' if len(errors) == 1 else ''} error{'s' if len(errors) > 1 else ''}:\n{'\n'.join(errors)}",
                    alert_type=AlertType.DANGER,
                    dismissed_automatically=False
                ), terminate_after_dismiss=True)
            )
            return

        self.app.call_from_thread(self.show_ledger_valid)

    def show_ledger_valid(self):
        from ui.screens.startup import BlockValidationScreen
        self.app.switch_screen(AlertScreen(UIAlert(
            title="Chain validation successful",
            message="The chain has been successfully validated.",
            alert_type=AlertType.SUCCESS
        ), callback=lambda: self.app.switch_screen(BlockValidationScreen()) if not self.close_after else self.app.pop_screen()))
