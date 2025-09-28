from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Digits

if __name__ == "__main__":
    app = ClockApp()
    app.run()