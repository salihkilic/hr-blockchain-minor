from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button


class UserLoginScreen(Screen):
    CSS_PATH = "UserForm.tcss"

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Please sign in", classes="title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Horizontal(
                Button("Login", id="login"),
                Button("Register", id="register"),
                classes="button-row",
            ),
            classes="form",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            self.app.pop_screen()
        if event.button.id == "register":
            self.app.push_screen("register_screen")