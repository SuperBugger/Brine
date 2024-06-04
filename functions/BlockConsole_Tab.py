from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.BlockConsole import BlockConsole
from functions.TreeListWidget import TreeListWidget


# Класс BlockConsole_Tab создает вкладку с функционалом блокировки консоли
class BlockConsole_Tab(QWidget):
    # Конструктор класса, инициализирует интерфейс
    def __init__(self):
        super().__init__()
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()
        # Создание виджета дерева
        self.tree_list_widget = TreeListWidget()
        # Создание виджета блокировки консоли
        self.selected_items_widget = BlockConsole(self.tree_list_widget)
        layout.addWidget(self.tree_list_widget)
        layout.addWidget(self.selected_items_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
