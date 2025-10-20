from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button


class UserRegisterScreen(Screen):
    CSS_PATH = "UserForm.tcss"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Please register", classes="title"),
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register":
            self.app.pop_screen()
        if event.button.id == "cancel":
            self.app.pop_screen()