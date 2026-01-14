import sys
import os
import random
from decimal import Decimal
import logging

# Setup basic logging to see internal logs (if any)
logging.basicConfig(level=logging.WARNING)

# Ensure we can import modules from src (current dir)
# Assuming script is run from project root or src
if os.path.exists("src"):
    sys.path.append(os.path.abspath("src"))
else:
    sys.path.append(os.getcwd())

try:
    from models import User, Transaction, Block
    from models.enum import TransactionType
    from blockchain import Pool
    from blockchain.ledger import Ledger
    from services import DifficultyService
    from blockchain.abstract_pickable_singleton import AbstractPickableSingleton
except ImportError:
    # If run from src directly
    sys.path.append(os.getcwd())
    from models import User, Transaction, Block
    from models.enum import TransactionType
    from blockchain import Pool
    from blockchain.ledger import Ledger
    from services import DifficultyService
    from blockchain.abstract_pickable_singleton import AbstractPickableSingleton

# --- Mocking / Setup ---

# Disable saving to disk
def no_op_save():
    pass

AbstractPickableSingleton._save = no_op_save
AbstractPickableSingleton.load = lambda: None

# Reset singleton state to ensure clean run
Ledger._instance = None
Pool._instance = None

# Initialize Ledger (creates Genesis block internally)
ledger = Ledger.get_instance()
print("Ledger initialized.")
latest_block = ledger.get_latest_block()
if latest_block:
    print(f"Genesis Block Hash: {latest_block.calculated_hash[:16]}... Difficulty: {latest_block.difficulty}")
else:
    print("Error: Genesis block not found.")
    sys.exit(1)

# Dummy Miner User
miner_user = User(
    username="miner",
    password_hash="dummy_hash",
    salt="dummy_salt",
    public_key="dummy_public_key",
    private_key="dummy_private_key",
    key_type="dummy_type"
)
print(f"Miner Address: {miner_user.address}")

# --- Mining Loop ---
NUM_BLOCKS = 50
print(f"\nStarting mining simulation for {NUM_BLOCKS} blocks...")
print(f"Target Time (DifficultyService): {DifficultyService.cfg.target_time}s")

for i in range(1, NUM_BLOCKS + 1):
    print(f"\n--- Mining Block #{i} ---")
    current_diff = DifficultyService.current_difficulty
    print(f"Current Difficulty: {current_diff} (Higher number = Easier)")

    # 1. Create Transactions (Signup Reward as fillers)
    # We need 5-10
    num_tx = random.randint(5, 10)
    transactions = []
    for j in range(num_tx):
        tx = Transaction(
            receiver_address=f"R_{i}_{j}".ljust(64, '0')[:64],
            amount=Decimal(50),
            fee=Decimal(0),
            kind=TransactionType.SIGNUP_REWARD,
            sender_address=None
        )
        transactions.append(tx)

    # 2. Mine Block
    try:
        new_block = Block.mine_with_transactions(miner_user, transactions)
    except Exception as e:
        print(f"Mining failed: {e}")
        import traceback
        traceback.print_exc()
        break

    print(f"Block mined in {new_block.mined_duration:.4f}s")
    print(f"Block Hash: {new_block.calculated_hash}")

    # 3. Update Ledger Mock
    ledger._blocks[new_block.calculated_hash] = new_block
    ledger._latest_block = new_block

    # 4. Check Result
    new_diff = DifficultyService.current_difficulty
    print(f"New Difficulty: {hex(new_diff)}")

    diff_change = new_diff - current_diff
    if diff_change > 0:
        print("Difficulty INCREASED (became EASIER)")
    elif diff_change < 0:
        print("Difficulty DECREASED (became HARDER)")
    else:
        print("Difficulty UNCHANGED")

print("\nSimulation complete.")
