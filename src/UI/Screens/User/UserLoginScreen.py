from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Placeholder, Static, Input, Button


class UserLoginScreen(Screen):
    CSS = """
        Screen {
            /* center everything in the screen */
            align: center middle;
        }

        /* the form card */
        .form {
            width: 100%;
            padding: 2;
            border: round $accent;
            background: $surface;
        }

        .title {
            padding-bottom: 1;
            content-align: center middle;
        }

        Input {
            margin-bottom: 1;
            border: heavy $accent;
        }

        Button {
            content-align: center middle;
            border: heavy $accent;
        }
        """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Please sign in", classes="title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Button("Login", id="login"),
            classes="form",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            self.app.pop_screen()  # Close the login screen on login button press