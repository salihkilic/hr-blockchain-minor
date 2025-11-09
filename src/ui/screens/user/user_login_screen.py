from textual import log
from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button, Label

from exceptions.user.invalid_credentials_exception import InvalidCredentialsException
from services.user_service import UserService


class UserLoginScreen(Screen):
    CSS_PATH = "UserForm.tcss"

    username: str = reactive("")
    password: str = reactive("")

    login_errors: list = reactive([], recompose=True)

    logged_in: bool = reactive(False, recompose=True)

    def __init__(self):
        super().__init__()
        user_service = UserService()
        if user_service.logged_in_user is not None:
            self.logged_in = True

    def compose(self) -> ComposeResult:

        user = UserService().logged_in_user

        if self.logged_in and user is not None:
            yield Vertical(
                Static(f"You are already logged in as {user.username}", classes="title"),
                Button("Continue", id="continue"),
                classes="form",
            )
            yield Footer()
            return

        log(f"Composing UserLoginScreen with errors: {self.login_errors}")

        error_labels = [Label(f"{error}", classes="login_error") for error in self.login_errors]

        yield Vertical(
            *error_labels,
            Static("Please sign in", classes="title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Horizontal(
                Button("Login", id="login"),
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
        if event.input.id == "password":
            self.password = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            self._try_logging_in()
        if event.button.id == "register":
            self.app.push_screen("register_screen")
        if event.button.id == "cancel":
            self.app.switch_mode("blockchain_explorer")
        if event.button.id == "continue":
            self.app.pop_screen()

    def _try_logging_in(self):
        user_service = UserService()
        self.login_errors = []
        log(f"Trying to log in user: {self.username}")
        try:
            user_service.login(self.username, self.password)
            log(f"Login successful for user: {self.username}")

            username_input = self.query_one("#username", Input)
            username_input.value = ""
            password_input = self.query_one("#password", Input)
            password_input.value = ""

            self.app.pop_screen()
        except InvalidCredentialsException as e:
            log(f"Login failed: {e}")
            self.login_errors = [str(e)]




