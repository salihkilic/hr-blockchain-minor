# hr-blockchain-minor

## Running the app

To run the Textual app, first install the development version of Textual in your terminal:

`pip install textual-dev`

Then run the Development Console with:

`textual console`

Install all requirements for the app with:
`pip install -r requirements.txt`

Go to the venv folder and activate the virtual environment with:
`.venv/Scripts/activate.bat`  (Windows)
or
`source .venv/bin/activate`  (MacOS / Linux)

And your app in another terminal window with:

`textual run --dev src/goodchain.py -- --node=1`

The `--node` argument specifies the node number to run.

### Some nice links:

- [Textual Documentation](https://textual.textualize.io/)
- [Textual Widgets](https://textual.textualize.io/widget_gallery/)
- [Video Tutorials](https://www.youtube.com/@Textualize)
- Examples:
    - [Textual Examples (How-To)](https://github.com/Textualize/textual/tree/main/docs/examples)
    - [Textual Examples (Demos)](https://github.com/Textualize/textual/tree/main/examples)

## Nodes

### Node data

Each node uses its own local data directory containing a private copy of the ledger and transaction pool. Nodes
synchronize these states through network communication and consensus, not by sharing files. The user database is shared
between nodes to provide consistent user and key management. For this assignment, a user is assumed to be logged in on
only one node at a time; concurrent logins with the same user are not supported and multi-login safety is intentionally
not implemented.

## Block consensus


In Part 2, each node runs independently with its own local copy of the ledger, pool, and user database.  
Synchronization between nodes is achieved through an explicit, cooperative consensus mechanism.

### Block Flow
1. A node mines a new block and broadcasts it to peers.
2. The block is marked as **pending** and is **not** immediately appended to the ledger.
3. Other nodes independently validate the block (PoW, transactions, previous hash).
4. Each validating node broadcasts a validation message for that block.
5. Once a block receives **three validations from distinct nodes** (excluding the miner), it becomes **finalized**.
6. Only finalized blocks are appended to the ledger and may be built upon.

### Key Properties
- No forks are allowed; mining is paused while a block is pending.
- Consensus is explicit and asynchronous: validations may arrive over time.
- Validation messages are not cryptographically signed; the system assumes honest nodes for simplicity.
- This model prioritizes clarity and determinism over adversarial security.

This approach satisfies the assignment requirement of syncing node data via a consensus mechanism while keeping the system simple and explainable.