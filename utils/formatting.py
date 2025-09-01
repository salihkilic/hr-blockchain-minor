# Utility functions
import random
import time

def _now() -> float:
    return time.time()

def _hash(prefix: str = "0x", length: int = 64) -> str:
    import secrets
    return prefix + secrets.token_hex(length // 2)

def _addr() -> str:
    return "0x" + ''.join(random.choices('0123456789abcdef', k=40))

def fmt_hash(h: str, head: int = 6, tail: int = 6) -> str:
    return f"{h[:2+head]}…{h[-tail:]}"

def fmt_age(ts: float) -> str:
    d = max(0, int(_now() - ts))
    if d < 60: return f"{d}s"
    if d < 3600: return f"{d//60}m"
    return f"{d//3600}h"

