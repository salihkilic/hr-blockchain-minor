from nicegui import ui

@ui.page('/transactions')
def other_page():
    ui.page_title('Transactions / Goodchain')

    ui.add_head_html('''
        <script>
          window.addEventListener('beforeunload', function (e) {
            e.preventDefault();
            e.returnValue = '';  // required for Chrome
          });
        </script>
        ''')

    # TODO Move this to a separate component
    with ui.row():
        ui.link('Dashboard', '/')
        ui.link('Transactions', '/transactions')

    ui.html('Transaction overview', tag='h1').classes('text-5xl font-bold')
