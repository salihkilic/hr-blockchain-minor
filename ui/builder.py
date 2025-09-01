# UI builder and layout (clean rewrite)
import dearpygui.dearpygui as dpg
from ui.callbacks import (
    refresh_metrics,
    refresh_plot,
    rebuild_blocks_table,
    do_search,
    on_add_txs,
    on_mine_block,
)
from ui.tags import (
    HEIGHT_TXT,
    AVG_TXT,
    TPS_TXT,
    MEMPOOL_TXT,
    TPS_SERIES,
    BLOCKS_TABLE,
    SEARCH_INPUT,
)

# Explicitly define __all__ for clarity
__all__ = ["build_ui"]

def build_ui():
    """Construct and run the Dear PyGui application main window."""
    dpg.create_context()
    dpg.create_viewport(title='BlockLite — DearPyGui Explorer (Demo)', width=1200, height=800)
    with dpg.window(label='Main', tag='main', width=1180, height=760, pos=(10,10)):
        # Top bar
        with dpg.group(horizontal=True):
            dpg.add_text('\u20bf Bitcoin Explorer (demo)')
            dpg.add_input_text(tag=SEARCH_INPUT, hint='block height/hash, txid, address', width=420, on_enter=True, callback=lambda s,a,u: do_search())
            dpg.add_button(label='Search', callback=lambda: do_search())
            dpg.add_spacer(width=12)
            dpg.add_button(label='Add TX burst', callback=lambda: on_add_txs())
            dpg.add_button(label='Mine block', callback=lambda: on_mine_block())
        dpg.add_separator()
        dpg.add_text('', tag='status_bar')
        # Metric tiles
        with dpg.group(horizontal=True):
            for label, tag in (
                ('Latest Block', HEIGHT_TXT),
                ('Avg Block Time', AVG_TXT),
                ('TPS (est.)', TPS_TXT),
                ('Mempool', MEMPOOL_TXT),
            ):
                with dpg.child_window(width=270, height=80):
                    dpg.add_text(label)
                    dpg.add_spacer(height=4)
                    dpg.add_text('-', tag=tag)
        # TPS Plot
        with dpg.plot(label='Throughput (TPS)', height=300, width=-1):
            dpg.add_plot_axis(dpg.mvXAxis, label='Block', tag='xaxis')
            with dpg.plot_axis(dpg.mvYAxis, label='TPS'):
                dpg.add_line_series([], [], label='TPS', tag=TPS_SERIES)
        # Latest Blocks Table
        dpg.add_text('Latest Blocks')
        with dpg.table(tag=BLOCKS_TABLE, header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp, height=360):
            for c in ('HEIGHT','TIME','AGE','TTM','MINER','N(TX)','VOLUME','FEE RANGE','Σ FEES','% FULL'):
                dpg.add_table_column(label=c)
    # Start
    dpg.setup_dearpygui()
    dpg.show_viewport()
    refresh_metrics(); refresh_plot(); rebuild_blocks_table()
    dpg.set_primary_window('main', True)
    print('[build_ui] starting DearPyGui event loop')
    dpg.start_dearpygui()
    print('[build_ui] DearPyGui loop exited')
    dpg.destroy_context()
