# Network catch-up

> For the network catch-up for the large part the existing "entrypoints" are used, that are also used in the live sync.

## Request flow

### Blocks

1. A - Request block after N
2. B - Sends block after N (including validations)
3. A - Validates and adds block to ledger (pending or accepted)
    1. Invalid blocks are ignored
4. A - Requests block after N + 1
5. Step 2 continues until B has no more blocks to send

> Transaction fairness is not checked on the side of A because the pool might not be intact anymore

### Transactions

1. A - Request for pool sync
2. B - Sends all transactions in pool, one by one
3. A - Receives all the transactions
    1. Known transactions are ignored
    2. Unknown transactions are validated
        1. Valid transaction are added
        2. Invalid transactions are ignored

### Validations

> To prevent a situations where nodes have the same block pending individual validations can be synced

1. A - Request for validation sync
2. B - Sends all validations for pending block, one by one
3. A - Receives all validations
    1. Relevant validations are added to the pending block
    2. Irrelevant validations are ignored

## Volunteering information

To make nodes sync when a ahead node comes online after a behind node. The nodes volunteer (broadcast) all the
information from steps `2` once at startup, as if there was a request. The behind nodes will receive the required info
and ask for more where necessary.