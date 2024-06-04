from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


# Класс CustomHeader добавляет кнопку обновления в заголовок таблицы
class CustomHeader(QHeaderView):
    # Конструктор класса, инициализирует интерфейс
    def __init__(self, orientation, parent_widget, parent=None):
        super(CustomHeader, self).__init__(orientation, parent)

        self.parent_widget = parent_widget

        self.button = QPushButton()
        self.button.setIcon(QIcon('refresh.png'))
        self.button.setIconSize(QSize(16, 16))
        self.button.setFixedSize(24, 24)
        self.button.clicked.connect(self.on_button_clicked)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addItem(self.spacer)

        self.layout.addWidget(self.button)
        self.layout.setContentsMargins(0, 0, 0, 0)

    # Метод для обработки нажатия на кнопку обновления
    def on_button_clicked(self):
        self.parent_widget.get_structure()
