from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical
from textual.widgets import Static, Footer, DataTable


class BlockchainExplorer(Screen):
    """
    Blockchain Explorer widget - displays blockchain data and allows interaction with the chain.

    High-Level Plan:

    1. Chain Overview & Statistics
       - Total number of blocks
       - Total number of transactions across all blocks
       - Overall chain validation status (tamper detection)

    2. Block List Display
       - Sequential (list) display of all blocks (starting from Genesis Block 0)
       - For each block show:
            - Block ID,
            - Timestamp,
            - Number of transactions,
            - Visual indicator for block status: pending validation, validated (3+ flags), or rejected

    3. Individual Block Details
       - Block hash and previous block hash
       - Nonce value
       - All transactions within the block (5-10 transactions per block)
       ?- Mining reward transaction
       - Block validation flags status
       - Time until mined

    4. Transaction Details View
       - Sender (username/public key)
       - Receiver (username/public key)
       - Transaction value
       ?- Transaction fee
       - Digital signature
       - Transaction validation status

    5. Pending Transactions Pool View
       - List of transactions waiting to be mined
       - Number of valid vs invalid transactions
       - Transaction fees (to help miners decide)
       - Flagged/invalid transactions marked clearly

    6. Validation Tools
       - Button/option to validate entire blockchain
       - Button/option to validate specific block
       - Button/option to add validation flag to a valid block (for logged-in users)
       - Visual feedback on validation results
    """

    DEFAULT_CSS = """
    BlockchainExplorer {
        layout: vertical;
    }

    /* Header overview */
    #chain_overview {
        dock: top;
        height: 5; /* adjustable */
        padding: 0 1;
        content-align: left middle;
        background: $surface 5%;
        border: tall $primary;
    }

    /* Pending pool near bottom above footer */
    #pending_pool_container {
        dock: bottom;
        height: 10; /* adjustable */
        background: $boost;
        border: tall $panel;
    }

    #pending_pool_title {
        content-align: left middle;
        padding-left: 1;
    }

    #pending_pool_table {
        height: 1fr;
    }

    /* Main content fills remaining space */
    #main_content {
        layout: horizontal;
        height: 1fr;
    }

    /* Block list (left) */
    #block_list_container {
        width: 45%;
        min-width: 40;
        border: tall $panel;
        background: $surface 3%;
        layout: vertical;
    }

    #block_list_title, #block_details_title, #transaction_details_title {
        background: $surface 10%;
        text-style: bold;
        padding-left: 1;
        height: 3;
        content-align: left middle;
    }

    #block_list_table, #block_details_body, #transaction_details_body {
        height: 1fr;
    }

    /* Details side (right) */
    #details_side {
        layout: vertical;
        width: 1fr;
        border: tall $panel;
        background: $surface 2%;
        padding: 0;
    }

    #block_details_container, #transaction_details_container {
        layout: vertical;
        border: tall $panel;
        background: $surface 4%;
        height: 1fr;
        min-height: 8;
    }

    #block_details_container {
        height: 55%; /* ratio between block details and tx details */
    }

    #transaction_details_container {
        height: 45%;
    }

    DataTable {
        scrollbar-size-vertical: 1;
        scrollbar-size-horizontal: 1;
    }
    """

    def __init__(self, title: str = "Blockchain Explorer"):
        super().__init__()
        self.title = title
        # References to dynamic widgets for later updates
        self.block_list_table: DataTable | None = None
        self.pending_pool_table: DataTable | None = None
        # Detail views as Static placeholders (could be replaced with richer widgets)
        self.block_details_body: Static | None = None
        self.transaction_details_body: Static | None = None
        self.chain_stats: Static | None = None

    def compose(self) -> ComposeResult:  # type: ignore[override]
        # Chain overview & statistics header
        chain_overview = Static("Chain Overview: blocks=0 | tx=0 | status=OK", id="chain_overview")
        self.chain_stats = chain_overview
        yield chain_overview

        # Main content area (left block list, right details)
        with Container(id="main_content"):
            # Left: block list
            with Vertical(id="block_list_container"):
                yield Static("Blocks", id="block_list_title")
                block_table = DataTable(id="block_list_table", cursor_type="row")
                self.block_list_table = block_table
                yield block_table

            # Right: details side
            with Vertical(id="details_side"):
                # Block details (top right)
                with Vertical(id="block_details_container"):
                    yield Static("Block Details", id="block_details_title")
                    block_details = Static("Select a block to view details", id="block_details_body")
                    self.block_details_body = block_details
                    yield block_details
                # Transaction details (bottom right)
                with Vertical(id="transaction_details_container"):
                    yield Static("Transaction Details", id="transaction_details_title")
                    tx_details = Static("Select a transaction to view details", id="transaction_details_body")
                    self.transaction_details_body = tx_details
                    yield tx_details

        # Pending transactions pool (bottom strip above footer)
        with Vertical(id="pending_pool_container"):
            yield Static("Pending Transactions", id="pending_pool_title")
            pending_table = DataTable(id="pending_pool_table", cursor_type="row")
            self.pending_pool_table = pending_table
            yield pending_table

        # Footer (global nav/help keys etc.)
        yield Footer()

    # --- Setup & stub update methods ---
    def on_mount(self) -> None:
        self._setup_block_list_table()
        self._setup_pending_pool_table()
        # Example placeholder data
        self.populate_demo_data()

    def _setup_block_list_table(self) -> None:
        if self.block_list_table and not self.block_list_table.columns:
            self.block_list_table.add_columns("ID", "Timestamp", "Tx Count", "Status")

    def _setup_pending_pool_table(self) -> None:
        if self.pending_pool_table and not self.pending_pool_table.columns:
            self.pending_pool_table.add_columns("Tx ID", "From", "To", "Value", "Fee", "Validity")

    def populate_demo_data(self) -> None:
        """Populate placeholder demo content so the scaffold is visible."""
        if self.block_list_table:
            for i in range(5):
                self.block_list_table.add_row(str(i), f"2025-10-06T12:00:{i:02}", str(2 + i), "validated" if i % 2 else "pending")
        if self.pending_pool_table:
            for i in range(3):
                self.pending_pool_table.add_row(f"tx{i}", "alice", "bob", str(10 + i), "0.1", "valid")

    # --- Public API (stubs for future integration) ---
    def update_chain_overview(self, total_blocks: int, total_tx: int, status: str) -> None:
        if self.chain_stats:
            self.chain_stats.update(f"Chain Overview: blocks={total_blocks} | tx={total_tx} | status={status}")

    def set_block_details(self, details_text: str) -> None:
        if self.block_details_body:
            self.block_details_body.update(details_text)

    def set_transaction_details(self, details_text: str) -> None:
        if self.transaction_details_body:
            self.transaction_details_body.update(details_text)

    def add_block_row(self, block_id: int, timestamp: str, tx_count: int, status: str) -> None:
        if self.block_list_table:
            self.block_list_table.add_row(str(block_id), timestamp, str(tx_count), status)

    def add_pending_transaction(self, tx_id: str, sender: str, receiver: str, value: float, fee: float, validity: str) -> None:
        if self.pending_pool_table:
            self.pending_pool_table.add_row(tx_id, sender, receiver, str(value), str(fee), validity)

    # --- Event handlers (to be implemented later) ---
    # def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    #     """Handle selecting rows to populate the detail panels."""
    #     pass
