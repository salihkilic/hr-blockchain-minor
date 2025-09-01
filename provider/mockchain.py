# MockChain implementation
import random
from typing import List, Dict, Optional
from models.block import Block
from models.tx import Tx
from provider.interface import IProvider
from utils.formatting import _now, _hash, _addr

class MockChain(IProvider):
    def __init__(self) -> None:
        self.blocks: List[Block] = []
        self.mempool: List[Tx] = []
        self.balances: Dict[str, float] = {}
        self.height = 0
        random.seed(23)
        self._addresses = [_addr() for _ in range(300)]
        for a in self._addresses:
            self.balances[a] = round(50 + random.random() * 250, 6)
        for _ in range(8):
            self.add_random_txs(random.randint(400, 1500))
            self.mine()

    def latest_block_number(self) -> int:
        return self.height
    def recent_blocks(self, n=10) -> List[Block]:
        return list(reversed(self.blocks[-n:]))
    def recent_txs(self, n=20) -> List[Tx]:
        txs = [t for b in self.blocks for t in b.txs]
        return list(reversed(txs))[:n]
    def get_block(self, number: int) -> Optional[Block]:
        if 1 <= number <= self.height:
            return self.blocks[number - 1]
        return None
    def get_tx(self, h: str) -> Optional[Tx]:
        for t in self.mempool:
            if t.hash == h:
                return t
        for b in self.blocks:
            for t in b.txs:
                if t.hash == h:
                    return t
        return None
    def get_address(self, addr: str) -> Dict:
        txs_c = [t for b in self.blocks for t in b.txs if t.frm == addr or t.to == addr]
        txs_p = [t for t in self.mempool if t.frm == addr or t.to == addr]
        return {
            'address': addr,
            'balance': self.balances.get(addr, 0.0),
            'nonce': 0,
            'confirmed': list(reversed(txs_c))[:50],
            'pending': list(reversed(txs_p))[:50],
        }
    def avg_block_time(self, k=20) -> float:
        if len(self.blocks) < 2: return 12.0
        hist = [b.ttm for b in self.blocks[-k:]]
        return sum(hist) / len(hist)
    def tps(self, k=20) -> float:
        if not self.blocks: return 0.0
        window = self.blocks[-k:]
        total_tx = sum(len(b.txs) for b in window)
        total_time = sum(b.ttm for b in window)
        return total_tx / total_time if total_time else 0.0
    def mempool_size(self) -> int:
        return len(self.mempool)
    def add_random_txs(self, n: int) -> None:
        for _ in range(n):
            s = random.choice(self._addresses)
            r = random.choice(self._addresses)
            while r == s:
                r = random.choice(self._addresses)
            v = round(max(0.0001, random.random() * 0.5), 6)
            fee = round(0.00001 + random.random() * 0.0005, 6)
            self.mempool.append(Tx(_hash(), s, r, v, fee, _now(), 'pending'))
    def mine(self) -> Block:
        parent = self.blocks[-1].hash if self.blocks else _hash()
        b_hash = _hash()
        count = min(len(self.mempool), random.randint(500, 3000))
        chosen = [self.mempool.pop(0) for _ in range(count)]
        ts_prev = self.blocks[-1].timestamp if self.blocks else _now() - 15
        ttm = max(3.0, random.gauss(12.0, 3.5))
        ts = ts_prev + ttm
        miner = random.choice(self._addresses)
        for t in chosen:
            t.status = 'confirmed'
            t.block_number = self.height + 1
        b = Block(
            number=self.height + 1,
            hash=b_hash,
            parent_hash=parent,
            timestamp=ts,
            ttm=ttm,
            miner=miner,
            txs=chosen,
            gas_used=random.randint(5_000_000, 25_000_000),
            size=random.randint(500_000, 1_800_000),
        )
        self.blocks.append(b)
        self.height += 1
        return b

