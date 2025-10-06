from __future__ import annotations

from textual.widgets import Static
from textual.reactive import reactive


class ChainOverview(Static):
    """Header widget displaying high-level blockchain statistics.

    Enhancements:
    - Reactive fields (suggestion 2): total_blocks, total_tx, status automatically trigger re-render.
    - Status color styling (suggestion 1): status rendered in color (OK=green, WARNING=yellow, BROKEN=red, fallback bold).
    """

    # TODO SK: Reactive state, should look into this more
    # https://textual.textualize.io/guide/reactivity/
    total_blocks: int = reactive(0)
    total_tx: int = reactive(0)
    status: str = reactive("OK")

    STATUS_STYLES = {
        "OK": "green bold",
        "WARNING": "yellow bold",
        "BROKEN": "red bold",
    }

    DEFAULT_CSS = """
    ChainOverview {
        content-align: left middle;
        padding: 0 1;
    }
    """

    def __init__(self, total_blocks: int = 0, total_tx: int = 0, status: str = "OK", id: str = "chain_overview"):
        super().__init__(id=id)
        # Initialize reactive attributes
        self.total_blocks = total_blocks
        self.total_tx = total_tx
        self.status = status
        # Initial render
        self._refresh_text()

    # Internal formatting helper
    def _format(self) -> str:
        style = self.STATUS_STYLES.get(self.status.upper(), "bold")
        return (
            f"Chain Overview: blocks={self.total_blocks} | "
            f"tx={self.total_tx} | status=[{style}]{self.status}[/]"
        )

    def _refresh_text(self) -> None:
        self.update(self._format())

    # Watchers (invoked automatically when reactive attributes change)
    def watch_total_blocks(self, value: int) -> None:  # noqa: D401
        self._refresh_text()

    def watch_total_tx(self, value: int) -> None:  # noqa: D401
        self._refresh_text()

    def watch_status(self, value: str) -> None:  # noqa: D401
        self._refresh_text()

    # Public API
    def update_metrics(
        self,
        total_blocks: int | None = None,
        total_tx: int | None = None,
        status: str | None = None,
    ) -> None:
        if total_blocks is not None:
            self.total_blocks = total_blocks
        if total_tx is not None:
            self.total_tx = total_tx
        if status is not None:
            self.status = status
        # No need to call _refresh_text explicitly; watchers handle updates.

    # Convenience accessors (retain for clarity / external callers)
    @property
    def total_transactions(self) -> int:
        return self.total_tx
