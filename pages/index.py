from nicegui import ui
import time

@ui.page('/')
def index():
    ui.page_title('Dashboard / Goodchain')

    # TODO Move this to a separate component
    with ui.row():
        ui.link('Dashboard', '/')
        ui.link('Transactions', '/transactions')

    ui.html('GOODCHAIN', tag='h1').classes('text-5xl font-bold')
    ui.label('The best chain 🔗').classes('text-lg')

    with ui.row().classes('w-full gap-0'):
            with ui.timeline(side='right').classes('w-1/3 bg-gray-100 p-4 rounded-lg'):
                for _ in range(3):
                    ui.timeline_entry(title='Transaction #56f0e22c374b85ca884a527cdf381118899bda12',
                                      subtitle='May 07, 2021',
                                      icon='link')
                    ui.timeline_entry(title='Transaction #f295e0adcb081ca94f1ccc0cca2ad5f4f634ff3f',
                                      subtitle='May 14, 2021',
                                      icon='link')
                    ui.timeline_entry(title='Transation #fe2f723843863e4dade4415746495c16e3add3f9',
                                      subtitle='December 15, 2022',
                                      icon='link')

            with ui.column().classes('w-1/3 p-4'):
                ui.label('Welcome to Goodchain, the revolutionary blockchain platform designed to transform the way we conduct transactions and manage data. Our mission is to provide a secure, transparent, and efficient solution for individuals and businesses alike.').classes('text-lg mb-4')
                ui.label('At Goodchain, we believe in the power of decentralization and the potential of blockchain technology to create a more equitable and trustworthy digital ecosystem. Our platform leverages cutting-edge cryptographic techniques to ensure the integrity and security of every transaction, while our user-friendly interface makes it easy for anyone to participate in the blockchain revolution.').classes('text-lg mb-4')
                ui.label('Whether you are an individual looking to make secure peer-to-peer transactions or a business seeking to streamline your operations and enhance transparency, Goodchain has you covered. Join us on this exciting journey as we build a better future together, one block at a time.').classes('text-lg')

                ui.button('Start mining', on_click=lambda: ui.notify('⛏ Mining started!'))
                ui.button('Button that triggers a function', on_click=_some_function)

            with ui.column().classes('w-1/3 p-4'):



                ui.html('Property binding', tag='h2').classes('text-3xl font-bold')

                class Demo:
                    def __init__(self):
                        self.number = 1

                demo = Demo()
                ui.slider(min=1, max=25).bind_value(demo, 'number')

                ui.label().bind_text_from(demo, 'number', lambda v: f'Value: {v}')

                ui.html('Some graph', tag='h2').classes('text-3xl font-bold')

                ui.echart({
                    'xAxis': {'type': 'category'},
                    'yAxis': {'axisLabel': {':formatter': 'value => "$" + value'}},
                    'series': [{'type': 'line', 'data': [5, 8, 13, 21, 34, 55]}],
                })

                columns = [
                    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
                    {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
                ]
                rows = [
                    {'name': 'Alice', 'age': 18},
                    {'name': 'Bob', 'age': 21},
                    {'name': 'Carol'},
                ]
                ui.table(columns=columns, rows=rows, row_key='name')

def _some_function():
    ui.notify('This is a notification from a function')
    print('This is a print statement from a function')