from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical
from textual.widgets import Footer, Static
from UI.Widgets import (
    ChainOverview,
    BlockList,
    BlockDetails,
    BlockInfo,
    TransactionDetails,
    TransactionInfo,
    PendingPool,
    PendingTx,
)


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
    BlockchainExplorer { layout: vertical; }

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
    """

    def __init__(self, title: str = "Blockchain Explorer"):
        super().__init__()
        self.title = title
        # Widget references
        self.chain_overview: ChainOverview | None = None
        self.block_list: BlockList | None = None
        self.block_details: BlockDetails | None = None
        self.transaction_details: TransactionDetails | None = None
        self.pending_pool: PendingPool | None = None

    def compose(self) -> ComposeResult:  # type: ignore[override]
        # Header
        self.chain_overview = ChainOverview(total_blocks=0, total_tx=0, status="OK", id="chain_overview")
        yield self.chain_overview

        # Main content
        with Container(id="main_content"):
            with Vertical(id="block_list_container"):
                self.block_list = BlockList(id="block_list")
                yield self.block_list
            with Vertical(id="details_side"):
                with Vertical(id="block_details_container"):
                    self.block_details = BlockDetails(id="block_details")
                    yield Static("Block Details", id="block_details_title")
                    yield self.block_details
                with Vertical(id="transaction_details_container"):
                    self.transaction_details = TransactionDetails(id="transaction_details")
                    yield Static("Transaction Details", id="transaction_details_title")
                    yield self.transaction_details
        # Pending pool
        with Vertical(id="pending_pool_container"):
            self.pending_pool = PendingPool(id="pending_pool")
            yield self.pending_pool
        # Footer
        yield Footer()

    # --- Lifecycle ---
    def on_mount(self) -> None:
        self.populate_demo_data()

    # --- Demo data population ---
    def populate_demo_data(self) -> None:
        if self.block_list:
            for i in range(5):
                status = "validated" if i % 2 else "pending"
                self.block_list.add_block(i, f"2025-10-06T12:00:{i:02}", 2 + i, status)
        if self.pending_pool:
            for i in range(3):
                self.pending_pool.add_transaction(PendingTx(
                    tx_id=f"tx{i}", sender="alice", receiver="bob", value=10 + i, fee=0.1, validity="valid"
                ))

    # --- Public API (delegating to widgets) ---
    def update_chain_overview(self, total_blocks: int, total_tx: int, status: str) -> None:
        if self.chain_overview:
            self.chain_overview.update_metrics(total_blocks=total_blocks, total_tx=total_tx, status=status)

    def add_block_row(self, block_id: int, timestamp: str, tx_count: int, status: str) -> None:
        if self.block_list:
            self.block_list.add_block(block_id, timestamp, tx_count, status)

    def add_pending_transaction(self, tx_id: str, sender: str, receiver: str, value: float, fee: float, validity: str) -> None:
        if self.pending_pool:
            self.pending_pool.add_transaction(PendingTx(tx_id, sender, receiver, value, fee, validity))

    def set_block_details(self, details: BlockInfo) -> None:
        if self.block_details:
            self.block_details.set_block(details)

    def set_transaction_details(self, details: TransactionInfo) -> None:
        if self.transaction_details:
            self.transaction_details.set_transaction(details)

    # --- Message Handlers ---
    def on_block_list_block_selected(self, message: BlockList.BlockSelected) -> None:  # Block selected in list
        # For now create a demo BlockInfo (in real code fetch from model)
        demo = BlockInfo(
            block_id=message.block_id,
            hash=f"hash_{message.block_id:04}",
            prev_hash=f"hash_{message.block_id-1:04}" if message.block_id > 0 else "0" * 8,
            nonce=12345 + message.block_id,
            tx_count=5 + message.block_id,
            flags=3 if message.block_id % 2 else 1,
            mine_time_ms=250 + message.block_id * 10,
            status="validated" if message.block_id % 2 else "pending",
        )
        self.set_block_details(demo)
        # Reset transaction details placeholder
        if self.transaction_details:
            self.transaction_details.clear()

    def on_pending_pool_transaction_selected(self, message: PendingPool.TransactionSelected) -> None:  # Transaction selected
        demo = TransactionInfo(
            tx_id=message.tx_id,
            sender="alice",
            receiver="bob",
            value=12.5,
            fee=0.1,
            signature="abcdef0123456789deadbeef",
            status="valid",
        )
        self.set_transaction_details(demo)
