from __future__ import annotations

from typing import Iterable, Optional
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Static


@dataclass
class PendingTx:
    tx_id: str
    sender: str
    receiver: str
    value: float
    fee: float
    validity: str  # valid|invalid|flagged|pending


class PendingPool(Widget):
    """Widget encapsulating the pending transactions pool table.

    Emits:
        TransactionSelected(tx_id: str)
    """

    DEFAULT_CSS = """
    PendingPool {
        layout: vertical;
    }
    PendingPool > Static.title {
        background: $surface 10%;
        text-style: bold;
        padding-left: 1;
        height: 3;
        content-align: left middle;
    }
    PendingPool DataTable { height: 1fr; }
    """

    class TransactionSelected(Message):
        def __init__(self, sender: 'PendingPool', tx_id: str) -> None:
            self.tx_id = tx_id
            super().__init__(sender)

    def __init__(self, *, id: str = "pending_pool", title: str = "Pending Transactions") -> None:
        super().__init__(id=id)
        self._title_text = title
        self.table: DataTable = DataTable(id=f"{id}_table", cursor_type="row")

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static(self._title_text, classes="title")
        yield self.table

    def on_mount(self) -> None:
        if not self.table.columns:
            self.table.add_columns("Tx ID", "From", "To", "Value", "Fee", "Validity")

    # Public API
    # TODO SK: Use these methods to manipulate the underlying data until we have a proper data binding system
    def add_transaction(self, tx: PendingTx) -> None:
        self.table.add_row(tx.tx_id, tx.sender, tx.receiver, str(tx.value), str(tx.fee), tx.validity)

    def add_transactions(self, txs: Iterable[PendingTx]) -> None:
        for tx in txs:
            self.add_transaction(tx)

    def clear(self) -> None:
        self.table.clear()

    def update_transaction(self, tx_id: str, *, sender: Optional[str] = None, receiver: Optional[str] = None,
                           value: Optional[float] = None, fee: Optional[float] = None, validity: Optional[str] = None) -> None:
        for row_key, row in list(self.table.rows.items()):  # type: ignore[attr-defined]
            if row[0] == tx_id:
                new_row = [
                    row[0],
                    sender if sender is not None else row[1],
                    receiver if receiver is not None else row[2],
                    str(value) if value is not None else row[3],
                    str(fee) if fee is not None else row[4],
                    validity if validity is not None else row[5],
                ]
                self.table.update_row(row_key, new_row)
                break

    # Event bridging
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:  # type: ignore[override]
        try:
            row = self.table.get_row(event.row_key)
            self.post_message(self.TransactionSelected(self, row[0]))
        except Exception:
            pass

