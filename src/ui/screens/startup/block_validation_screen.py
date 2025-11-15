import time
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.screen import Screen
from textual.widgets import Footer, Label, LoadingIndicator

from blockchain import Ledger
from exceptions.mining import InvalidBlockException
from exceptions.transaction import InvalidTransactionException
from models.dto import UIAlert
from models.enum import AlertType
from services.user_service import UserService
from ui.screens.utils.alert_screen import AlertScreen


class BlockValidationScreen(Screen):
    DEFAULT_CSS = """
        Button {
            margin: 0 2;
        }
        BlockValidationScreen{
            margin: 2;
            padding: 1;
            height: 100%;
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
            Label("Automatically validating pending block", classes="title"),
            Container(
                LoadingIndicator(),
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        from ui.screens.startup import TransactionRemovalScreen

        pending_block = Ledger.get_instance().get_pending_block()
        validator = UserService.logged_in_user

        if pending_block is None:
            self.app.switch_screen(AlertScreen(UIAlert(
                title="No pending block found",
                message="There is no pending block to validate at this time. Skipping validation.",
                alert_type=AlertType.INFO
            ), callback=lambda: self.app.switch_screen(TransactionRemovalScreen())))
            return

        # Check if validator already validated the block
        validations = pending_block.validators

        if validator.address in list(map(lambda v: v.validator, validations)):
            self.app.switch_screen(AlertScreen(UIAlert(
                title="Block already validated",
                message="You have already validated the pending block. Skipping validation.",
                alert_type=AlertType.INFO
            ), callback=lambda: self.app.switch_screen(TransactionRemovalScreen())))
            return

        if pending_block.miner_address == validator.address:
            self.app.switch_screen(AlertScreen(UIAlert(
                title="Validator is the miner",
                message="You cannot validate a block that you have mined yourself. Skipping validation.",
                alert_type=AlertType.WARNING
            ), callback=lambda: self.app.switch_screen(TransactionRemovalScreen())))
            return

        self._validate_pending_block()

    @work(exclusive=True, thread=True)
    def _validate_pending_block(self):
        try:
            pending_block = Ledger.get_instance().get_pending_block()
            current_block = Ledger.get_instance().get_latest_block()
            validator = UserService.logged_in_user

            if pending_block is not None:
                time.sleep(1)
                result = pending_block.validate(current_block)

                if not result:
                    Ledger.get_instance().add_validation_flag(pending_block.calculated_hash, validator.address,
                                                              False, 'Block could not be validated.')
                    raise InvalidBlockException("Pending block is invalid.")

                if not result.valid:
                    # TODO Handle invalid transactions
                    Ledger.get_instance().add_validation_flag(pending_block.calculated_hash, validator.address,
                                                              result.valid, '\n'.join(result.reasons))
                    raise InvalidBlockException('\n'.join(result.reasons))

                Ledger.get_instance().add_validation_flag(pending_block.calculated_hash, validator.address,
                                                          result.valid)
        except (InvalidBlockException, InvalidTransactionException) as e:
            from ui.screens.startup import TransactionRemovalScreen
            self.app.call_from_thread(
                self.app.switch_screen,
                AlertScreen(UIAlert(
                    title="Block validation failed",
                    message=f"The block validation failed due to error:\n{e}",
                    alert_type=AlertType.WARNING,
                    dismissed_automatically=False
                ), callback=lambda: self.app.switch_screen(TransactionRemovalScreen()))
            )
            return

            # success case
        self.app.call_from_thread(self.show_ledger_valid)

    def show_ledger_valid(self):
        from ui.screens.startup import TransactionRemovalScreen
        self.app.switch_screen(AlertScreen(UIAlert(
            title="Block validation successful",
            message="The pending block has been successfully validated.",
            alert_type=AlertType.SUCCESS
        ), callback=lambda: self.app.switch_screen(TransactionRemovalScreen())))
