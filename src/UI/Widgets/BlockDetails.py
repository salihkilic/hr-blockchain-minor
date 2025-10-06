from __future__ import annotations

from dataclasses import dataclass
from textual.widgets import Static
from textual.reactive import reactive


@dataclass
class BlockInfo:
    block_id: int
    hash: str
    prev_hash: str
    nonce: int
    tx_count: int
    flags: int | None = None
    mine_time_ms: int | None = None
    status: str = "pending"  # pending|validated|rejected


class BlockDetails(Static):
    """Widget showing details for a single block.

    Public API:
        set_block(BlockInfo)
        clear()
    """

    info: BlockInfo | None = reactive(None)

    DEFAULT_CSS = """
    BlockDetails {
        padding: 0 1;
        content-align: left top;
    }
    BlockDetails > .title {
        background: $surface 10%;
        text-style: bold;
        height: 3;
        content-align: left middle;
        padding-left: 1;
    }
    """

    STATUS_STYLES = {
        "PENDING": "yellow",
        "VALIDATED": "green",
        "REJECTED": "red",
    }

    def __init__(self, id: str = "block_details"):
        super().__init__(id=id)
        self.update(self._placeholder())

    # This is nice: You can use this for "temporary placeholder" text when no block is selected
    def _placeholder(self) -> str:
        return "[dim]Select a block to view details[/]"

    def watch_info(self, value: BlockInfo | None) -> None:
        if value is None:
            self.update(self._placeholder())
        else:
            self.update(self._format_info(value))

    def _format_info(self, info: BlockInfo) -> str:
        status_style = self.STATUS_STYLES.get(info.status.upper(), "bold")
        parts = [
            f"[b]Block[/b] #{info.block_id}",
            f"Status: [{status_style}]{info.status}[/]  Tx: {info.tx_count}  Nonce: {info.nonce}",
            f"Hash: [dim]{info.hash}[/]",
            f"Prev: [dim]{info.prev_hash}[/]",
        ]
        if info.flags is not None:
            parts.append(f"Flags: {info.flags}")
        if info.mine_time_ms is not None:
            parts.append(f"Mine time: {info.mine_time_ms} ms")
        return "\n".join(parts)

    # Public API
    def set_block(self, info: BlockInfo) -> None:
        self.info = info

    def clear(self) -> None:
        self.info = None

