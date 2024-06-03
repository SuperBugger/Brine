from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.AddRepository import AddRepository
from functions.Repositorynppct import Repositorynppct


class Repository_Сonnecnt(QWidget):
    def __init__(self, tree_widget):
        super().__init__()

        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        self.text_edit = QTextEdit(self)
        self.add_button = QPushButton('Добавить репозитории', self)
        self.add_button.setEnabled(False)

        self.text_label = QLabel('Введите список репозиториев:', self)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.text_label)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.add_button)

        self.scroll_area = QScrollArea()
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)
        layout.addWidget(self.scroll_area)

        self.my_widget = AddRepository(self.text_edit, self.add_button, self.tree_widget, self.label, self.scroll_area)
        self.my_widget.setLayout(layout)

        self.repo_widget = Repositorynppct(self.tree_widget, self.label, self.scroll_area)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.my_widget)
        main_layout.addWidget(self.repo_widget)

        self.text_edit.textChanged.connect(self.my_widget.enable_button)
        self.add_button.clicked.connect(self.my_widget.print_text)

        self.show()
