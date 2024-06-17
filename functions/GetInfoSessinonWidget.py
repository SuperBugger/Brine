from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.TreeListWidget import TreeListWidget
from functions.ScenarioWidget import scenarioWidget


class GetInfoSessinonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        tree_list_widget = TreeListWidget()
        self.selected_items_widget = scenarioWidget(tree_list_widget, "brine.get_user_sessions")
        layout.addWidget(tree_list_widget)
        layout.addWidget(self.selected_items_widget)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
