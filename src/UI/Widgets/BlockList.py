from __future__ import annotations

from typing import Iterable, Optional

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import DataTable, Static
from textual.widget import Widget


class BlockList(Widget):
    """Widget encapsulating the block summary table.

    Emits:
        BlockSelected(block_id: int)
    """

    DEFAULT_CSS = """
    BlockList {
        layout: vertical;
    }
    BlockList > Static.title {
        background: $surface 10%;
        text-style: bold;
        padding-left: 1;
        height: 3;
        content-align: left middle;
    }
    BlockList DataTable {
        height: 1fr;
    }
    """

    class BlockSelected(Message):
        def __init__(self, sender: 'BlockList', block_id: int) -> None:
            self.block_id = block_id
            super().__init__(sender)

    def __init__(self, *, id: str = "block_list", title: str = "Blocks") -> None:
        super().__init__(id=id)
        self._title_text = title
        self.table: DataTable = DataTable(id=f"{id}_table", cursor_type="row")

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static(self._title_text, classes="title")
        yield self.table

    def on_mount(self) -> None:
        if not self.table.columns:
            self.table.add_columns("ID", "Timestamp", "Tx Count", "Status")

    # Public API
    # TODO SK: Use these methods to manipulate the block list table until we have a proper data binding system
    def add_block(self, block_id: int, timestamp: str, tx_count: int, status: str) -> None:
        self.table.add_row(str(block_id), timestamp, str(tx_count), status)

    def add_blocks(self, blocks: Iterable[tuple[int, str, int, str]]) -> None:
        for b in blocks:
            self.add_block(*b)

    def clear_blocks(self) -> None:
        self.table.clear()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        try:
            row = self.table.get_row(event.row_key)
            block_id = int(row[0])
            self.post_message(self.BlockSelected(self, block_id))
        except Exception:
            pass

