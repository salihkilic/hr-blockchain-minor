"""
BlockLite — a simple blockchain explorer UI in Dear PyGui (demo)
Inspired by mempool-style layout: search bar, metric tiles, TPS plot, latest blocks table,
plus basic detail popups for Block / Tx / Address.

Quick start:
  pip install dearpygui
  python app.py

Notes:
- Uses a MockChain provider for offline demo data.
- Click a HEIGHT cell in the table to open Block details.
- Use the buttons to add tx bursts or mine a new block (kept simple on purpose).
- Swap MockChain for a real provider by implementing IProvider and wiring into build_ui().
"""
import importlib, sys
import ui as ui_pkg
print('[debug] imported ui module from:', getattr(ui_pkg, '__file__', 'NOFILE'))
from ui.builder import build_ui
print('[debug] build_ui object:', build_ui)

if __name__ == '__main__':
    build_ui()
