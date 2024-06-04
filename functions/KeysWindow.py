from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


# Класс KeysWindow отвечает за отображение ключей
class KeysWindow(QDialog):
    def init(self, parent=None):
        super().init(parent)
        self.setWindowTitle("Ключи конфигурации")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Здесь добавляем элементы, которые будут отображать ключи
        self.keys_label = QLabel("Здесь будут отображены ключи конфигурации")
        layout.addWidget(self.keys_label)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
