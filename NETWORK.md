# Networking & Synchronization Flows

## Transaction Creation & Propagation

1. **Transaction creation (Node A)**
   1. A user creates a transaction on Node A.
   2. Node A validates the transaction locally.
   3. The transaction is added to Node A’s local transaction pool.

2. **Transaction broadcast (Node A)**
   1. Node A broadcasts the transaction.
   2. Topic: `transactions.broadcast`
   3. Payload contains the serialized transaction data.

3. **Transaction reception (Node B)**
   1. Node B receives the `transactions.broadcast` message.
   2. Node B parses the payload.
   3. Node B validates the transaction.

4. **Transaction storage (Node B)**
   1. If valid, the transaction is added to Node B’s local transaction pool.
   2. If invalid, the transaction is ignored or flagged.

---

## Transaction Pool Synchronization (Late Join / Recovery)

1. **Startup or desync detection (Node B)**
   1. Node B starts or detects that its pool may be outdated.

2. **Pool request (Node B)**
   1. Node B sends a pool snapshot request.
   2. Topic: `transactions.pool.request`.

3. **Pool response (Node A or peer)**
   1. A peer receives the request.
   2. The peer responds with the full transaction pool.
   3. Topic: `transactions.pool.response`.
   4. Payload contains a list of transactions.

4. **Pool rebuild (Node B)**
   1. Node B validates all received transactions.
   2. Valid transactions are added to the local pool.
   3. Invalid transactions are discarded.

---

## Block Mining & Propagation

1. **Block mining (Node A)**
   1. Node A selects valid transactions from its local pool.
   2. Node A mines a new block.
   3. The block is validated locally.

2. **Block broadcast (Node A)**
   1. Node A broadcasts the new block.
   2. Topic: `blocks.broadcast`.
   3. Payload contains the block number and block data.

3. **Block reception (Node B)**
   1. Node B receives the `blocks.broadcast` message.
   2. Node B validates the block and its transactions.

4. **Ledger update (Node B)**
   1. If valid, the block is appended to Node B’s local ledger.
   2. Transactions included in the block are removed from Node B’s local pool.

---

## Ledger Synchronization (Offline Node Catch-Up)

1. **Out-of-sync detection (Node B)**
   1. Node B detects missing blocks in its local ledger.

2. **Block request (Node B)**
   1. Node B requests the next block after its latest known block.
   2. Topic: `blocks.sync.request`.
   3. Payload includes the last known block number.

3. **Block response (Node A or peer)**
   1. A peer receives the request.
   2. The peer responds with the next block.
   3. Topic: `blocks.sync.response`.

4. **Block application (Node B)**
   1. Node B validates the received block.
   2. If valid, the block is appended to the local ledger.
   3. Steps 2–4 repeat until the ledger is fully synchronized.

---

## Design Assumptions

1. Broadcast messages are best-effort and may be missed.
2. Nodes may go offline at any time.
3. Explicit request/response synchronization ensures eventual consistency.
4. Validation and consensus logic are implemented outside the networking layer.
5. The networking layer is responsible only for message transport and routing.
