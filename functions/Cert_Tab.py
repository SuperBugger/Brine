from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CertCopy import CertCopy
from functions.TreeListWidget import TreeListWidget


# Класс Cert_Tab создает вкладку с функционалом копирования сертификатов
class Cert_Tab(QWidget):
    # Конструктор класса, инициализирует интерфейс
    def __init__(self):
        super().__init__()
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()
        # Создание виджета дерева
        self.tree_list_widget = TreeListWidget()  # Изменено добавлено self
        # Создание виджета копирования сертификатов
        self.selected_items_widget = CertCopy(self.tree_list_widget)  # Изменено добавлено self
        layout.addWidget(self.tree_list_widget)  # Изменено добавлено self
        layout.addWidget(self.selected_items_widget)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
