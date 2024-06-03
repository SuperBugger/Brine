from PyQt5.QtWidgets import *

from functions.Repository_Disconnect import Repository_Disconnect
from functions.Repository_Сonnecnt import Repository_Сonnecnt
from functions.TreeListWidget import TreeListWidget


class Repository_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        tab_container = QTabWidget()

        connect_tab = QWidget()
        connect_layout = QVBoxLayout()
        tree_list_widget_connect = TreeListWidget()
        selected_items_widget = Repository_Сonnecnt(tree_list_widget_connect)
        connect_layout.addWidget(tree_list_widget_connect)
        connect_layout.addWidget(selected_items_widget)
        connect_tab.setLayout(connect_layout)

        disconnect_tab = QWidget()
        disconnect_layout = QVBoxLayout()
        tree_list_widget_disconnect = TreeListWidget()
        disconnect_widget = Repository_Disconnect(tree_list_widget_disconnect)
        disconnect_layout.addWidget(tree_list_widget_disconnect)
        disconnect_layout.addWidget(disconnect_widget)
        disconnect_tab.setLayout(disconnect_layout)

        tab_container.addTab(connect_tab, 'Подключить')
        tab_container.addTab(disconnect_tab, 'Отключить')

        layout = QVBoxLayout()
        layout.addWidget(tab_container)
        self.setLayout(layout)
