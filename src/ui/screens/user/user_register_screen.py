from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button, Label

from exceptions.user import DuplicateUsernameException
from models.dto import UIAlert
from models.enum import AlertType
from ui.screens.utils import AlertScreen


class UserRegisterScreen(Screen):
    DEFAULT_CSS = """
        .title {
          margin: 2 4;
        }
        
        Input {
          margin: 2 4;
        }
        
        Button {
          margin: 0 2 0 4;
        }
        
        .login_error{
            color: red;
            margin: 2 4;
        }
    """

    username: str = reactive("")
    password: str = reactive("")
    password_reenter: str = reactive("")

    errors: list = reactive([], recompose=True)

    def compose(self) -> ComposeResult:

        error_labels = [Label(f"{error}", classes="login_error") for error in self.errors]

        yield Vertical(
            *error_labels,
            Label("Please register", classes="title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Input(placeholder="Re-enter Password", password=True, id="password_reenter"),
            Horizontal(
                Button("Register", id="register"),
                Button("Cancel", id="cancel"),
                classes="button-row",
            ),
            classes="form",
        )
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "username":
            self.username = event.value
        elif event.input.id == "password":
            self.password = event.value
        elif event.input.id == "password_reenter":
            self.password_reenter = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register":
            self._try_register()
        if event.button.id == "cancel":
            self.app.pop_screen()

    def _try_register(self):

        if self.username.strip() == "":
            self.errors = ["Username cannot be empty"]
            return

        if self.password == "":
            self.errors = ["Password cannot be empty"]
            return

        if self.password != self.password_reenter:
            self.errors = ["Passwords do not match"]
            return

        from services.user_service import UserService
        user_service = UserService()

        try:
            user_service.register(self.username, self.password)
        except DuplicateUsernameException:
            self.errors = ["Username already exists"]
            self._clear_inputs()
            return

        self._clear_inputs()

        self.app.switch_screen(AlertScreen(UIAlert(
            title="Registration successful",
            message="You have been registered successfully. You can now log in.",
            alert_type=AlertType.SUCCESS
        )))

    def _clear_inputs(self):
        username_input = self.query_one("#username", Input)
        username_input.value = ""
        password_input = self.query_one("#password", Input)
        password_input.value = ""
        password_reenter_input = self.query_one("#password_reenter", Input)
        password_reenter_input.value = ""
