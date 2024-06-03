from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.Schedule import Schedule
from functions.TreeListWidget import TreeListWidget


class Timetable_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tree_list_widget = TreeListWidget()
        schedule_widget = Schedule(tree_list_widget)
        layout.addWidget(tree_list_widget)
        layout.addWidget(schedule_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
