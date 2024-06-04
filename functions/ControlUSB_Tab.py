from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.ControlUSB import ControlUSB
from functions.TreeListWidget import TreeListWidget


# Класс ControlUSB_Tab создает вкладку с функционалом управления USB
class ControlUSB_Tab(QWidget):
    # Конструктор класса, инициализирует интерфейс
    def __init__(self):
        super().__init__()
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()
        # Создание виджета дерева
        tree_list_widget = TreeListWidget()
        # Создание виджета управления USB
        self.selected_items_widget = ControlUSB(tree_list_widget)
        layout.addWidget(tree_list_widget)
        layout.addWidget(self.selected_items_widget)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
