from __future__ import annotations

from dataclasses import dataclass
from textual.widgets import Static
from textual.reactive import reactive


@dataclass
class TransactionInfo:
    tx_id: str
    sender: str
    receiver: str
    value: float
    fee: float | None = None
    signature: str | None = None
    status: str = "valid"  # valid|invalid|pending


class TransactionDetails(Static):
    """Widget showing details of a single transaction."""

    info: TransactionInfo | None = reactive(None)

    DEFAULT_CSS = """
    TransactionDetails {
        padding: 0 1;
        content-align: left top;
    }
    TransactionDetails > .title {
        background: $surface 10%;
        text-style: bold;
        height: 3;
        content-align: left middle;
        padding-left: 1;
    }
    """

    STATUS_STYLES = {
        "VALID": "green",
        "INVALID": "red",
        "PENDING": "yellow",
    }

    def __init__(self, id: str = "transaction_details"):
        super().__init__(id=id)
        self.update(self._placeholder())

    def _placeholder(self) -> str:
        return "[dim]Select a transaction to view details[/]"

    def watch_info(self, value: TransactionInfo | None) -> None:
        if value is None:
            self.update(self._placeholder())
        else:
            self.update(self._format_info(value))

    def _format_info(self, info: TransactionInfo) -> str:
        status_style = self.STATUS_STYLES.get(info.status.upper(), "bold")
        parts = [
            f"[b]Transaction[/b] {info.tx_id}",
            f"Status: [{status_style}]{info.status}[/]  Value: {info.value}  Fee: {info.fee if info.fee is not None else '-'}",
            f"From: {info.sender}",
            f"To:   {info.receiver}",
        ]
        if info.signature:
            sig_short = info.signature[:16] + "..." if len(info.signature) > 19 else info.signature
            parts.append(f"Signature: [dim]{sig_short}[/]")
        return "\n".join(parts)

    # Public API
    def set_transaction(self, info: TransactionInfo) -> None:
        self.info = info

    def clear(self) -> None:
        self.info = None

