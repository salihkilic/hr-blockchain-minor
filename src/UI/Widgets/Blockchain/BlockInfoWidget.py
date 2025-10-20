from textual.app import RenderResult, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Rule, Button, Static, ListView, ListItem


class BlockInfoWidget(Widget):
    CSS = """
        .block_info__title{
            height: 3;
            background: $accent;
            color: $text;
            text-style: bold;
        }
        Button{
            width: 50%;
        }
        .transactions_scroll{
            height: 20;
            border: solid $accent;
        }
        """

    def compose(self) -> ComposeResult:
        visible_block = 23

        txs = [ListItem(Label(f"NORMAL | Transaction {i+1}: From Alice to Bob - Amount: {10 + i} GCN"), classes="transaction") for i in range(15)]

        yield Vertical(
            Label(f"Block #{visible_block}"),
            Rule(line_style="heavy"),
            Horizontal(
                Button("Previous Block", id="prev_block"),
                Button("Next Block", id="next_block", disabled=True),
                classes="button-row"
            ),
            ListView(
                *txs,
                classes="transactions_scroll"
            )
        )