# UI callbacks and state
import dearpygui.dearpygui as dpg
from provider.mockchain import MockChain
from utils.formatting import fmt_hash, fmt_age
from ui.tags import HEIGHT_TXT, AVG_TXT, TPS_TXT, MEMPOOL_TXT, TPS_SERIES, BLOCKS_TABLE, SEARCH_INPUT
import time
import random

provider = MockChain()

def refresh_metrics():
    dpg.set_value(HEIGHT_TXT, str(provider.latest_block_number()))
    dpg.set_value(AVG_TXT, f"{provider.avg_block_time():.2f}s")
    dpg.set_value(TPS_TXT, f"{provider.tps():.2f}")
    dpg.set_value(MEMPOOL_TXT, str(provider.mempool_size()))

def refresh_plot():
    rec = provider.recent_blocks(40)
    xs = [b.number for b in rec]
    ys = [max(0.01, len(b.txs)/max(1.0, b.ttm)) for b in rec]
    dpg.configure_item(TPS_SERIES, x=xs, y=ys)

def rebuild_blocks_table():
    rows = dpg.get_item_children(BLOCKS_TABLE, 1) or []
    for r in rows:
        dpg.delete_item(r)
    cols = (
        'HEIGHT','TIME','AGE','TTM','MINER','N(TX)','VOLUME','FEE RANGE','Σ FEES','% FULL'
    )
    for b in provider.recent_blocks(12):
        with dpg.table_row(parent=BLOCKS_TABLE):
            dpg.add_selectable(label=str(b.number), callback=lambda s,a,u=b.number: open_block(u))
            dpg.add_text(time.strftime('%I:%M %p', time.localtime(b.timestamp)))
            dpg.add_text(fmt_age(b.timestamp))
            dpg.add_text(f"{b.ttm:.0f}s")
            dpg.add_text(fmt_hash(b.miner, 6, 4))
            dpg.add_text(str(len(b.txs)))
            dpg.add_text(f"{sum(t.value for t in b.txs):.3f}")
            fee_min = min((t.fee for t in b.txs), default=0.0)
            fee_max = max((t.fee for t in b.txs), default=0.0)
            dpg.add_text(f"{fee_min:.4f}, {fee_max:.4f}")
            dpg.add_text(f"{sum(t.fee for t in b.txs):.4f}")
            full = min(99, int(b.gas_used / b.gas_limit * 100))
            dpg.add_text(f"{full}%")

def open_block(number: int):
    b = provider.get_block(number)
    if not b:
        dpg.configure_item('status_bar', default_value='Block not found')
        return
    tag = f"block_win_{number}"
    if dpg.does_item_exist(tag):
        dpg.set_primary_window(tag, True)
        dpg.focus_item(tag)
        return
    with dpg.window(label=f"Block #{b.number}", tag=tag, width=860, height=520, pos=(80,80), on_close=lambda: dpg.delete_item(tag)):
        dpg.add_text(f"Hash: {b.hash}")
        dpg.add_text(f"Parent: {b.parent_hash}")
        dpg.add_text(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(b.timestamp))} ({fmt_age(b.timestamp)} ago)")
        dpg.add_text(f"Time to mine: {b.ttm:.2f}s")
        dpg.add_text(f"Miner: {b.miner}")
        dpg.add_text(f"Gas Used: {b.gas_used:,} / {b.gas_limit:,}")
        dpg.add_text(f"Size: {b.size:,} bytes")
        dpg.add_spacer(height=6)
        dpg.add_text(f"Transactions ({len(b.txs)})")
        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp, height=-1):
            for c in ('HASH','AGE','FROM','TO','VALUE','FEE','STATUS'):
                dpg.add_table_column(label=c)
            for t in b.txs:
                with dpg.table_row():
                    dpg.add_text(fmt_hash(t.hash))
                    dpg.add_text(fmt_age(t.timestamp))
                    dpg.add_text(fmt_hash(t.frm, 6, 4))
                    dpg.add_text(fmt_hash(t.to, 6, 4))
                    dpg.add_text(f"{t.value:.6f}")
                    dpg.add_text(f"{t.fee:.6f}")
                    dpg.add_text(t.status)

def open_tx(h: str):
    t = provider.get_tx(h)
    with dpg.window(label='Transaction', width=700, height=360, pos=(120,120)):
        if not t:
            dpg.add_text('Transaction not found')
            return
        dpg.add_text(f"Hash: {t.hash}")
        dpg.add_text(f"Status: {t.status}")
        dpg.add_text(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t.timestamp))} ({fmt_age(t.timestamp)} ago)")
        dpg.add_text(f"From: {t.frm}")
        dpg.add_text(f"To: {t.to}")
        dpg.add_text(f"Value: {t.value:.6f}")
        dpg.add_text(f"Fee: {t.fee:.6f}")
        dpg.add_text(f"Block: {t.block_number or '(pending)'}")

def open_address(addr: str):
    info = provider.get_address(addr)
    with dpg.window(label=f"Address {info['address']}", width=900, height=600, pos=(100,100)):
        dpg.add_text(f"Balance: {info['balance']:.6f}")
        dpg.add_text(f"Nonce: {info['nonce']}")
        dpg.add_text(f"Pending: {len(info['pending'])}")
        dpg.add_spacer(height=6)
        dpg.add_text('Confirmed')
        with dpg.table(header_row=True, resizable=True, height=240):
            for c in ('HASH','AGE','FROM','TO','VALUE','FEE','STATUS'):
                dpg.add_table_column(label=c)
            for t in info['confirmed']:
                with dpg.table_row():
                    dpg.add_text(fmt_hash(t.hash))
                    dpg.add_text(fmt_age(t.timestamp))
                    dpg.add_text(fmt_hash(t.frm, 6, 4))
                    dpg.add_text(fmt_hash(t.to, 6, 4))
                    dpg.add_text(f"{t.value:.6f}")
                    dpg.add_text(f"{t.fee:.6f}")
                    dpg.add_text(t.status)
        dpg.add_spacer(height=6)
        dpg.add_text('Pending')
        with dpg.table(header_row=True, resizable=True, height=200):
            for c in ('HASH','AGE','FROM','TO','VALUE','FEE','STATUS'):
                dpg.add_table_column(label=c)
            for t in info['pending']:
                with dpg.table_row():
                    dpg.add_text(fmt_hash(t.hash))
                    dpg.add_text(fmt_age(t.timestamp))
                    dpg.add_text(fmt_hash(t.frm, 6, 4))
                    dpg.add_text(fmt_hash(t.to, 6, 4))
                    dpg.add_text(f"{t.value:.6f}")
                    dpg.add_text(f"{t.fee:.6f}")
                    dpg.add_text(t.status)

def do_search():
    s = (dpg.get_value(SEARCH_INPUT) or '').strip()
    if not s:
        dpg.configure_item('status_bar', default_value='Enter a block number, tx hash, or address')
        return
    if s.isdigit():
        open_block(int(s)); return
    if len(s) > 50:
        open_tx(s); return
    open_address(s)

def on_add_txs():
    provider.add_random_txs(random.randint(300, 1200))
    refresh_metrics()

def on_mine_block():
    provider.mine()
    refresh_metrics(); refresh_plot(); rebuild_blocks_table()

