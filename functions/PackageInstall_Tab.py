from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.PackageInstal import PackageInstal
from functions.TreeListWidget import TreeListWidget


class PackageInstall_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        tree_list_widget = TreeListWidget()
        self.selected_items_widget = PackageInstal(tree_list_widget)
        layout.addWidget(tree_list_widget)
        layout.addWidget(self.selected_items_widget)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)