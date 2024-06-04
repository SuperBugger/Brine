from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.BlockProgram import BlockProgram
from functions.TreeListWidget import TreeListWidget


# Класс BlockProgramm_Tab создает вкладку с функционалом блокировки программ
class BlockProgramm_Tab(QWidget):
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
        self.selected_items_widget = BlockProgram(self.tree_list_widget)
        layout.addWidget(self.tree_list_widget)
        layout.addWidget(self.selected_items_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

