from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class BlockSession(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        host_label = QLabel("Хост:")
        self.host_input = QLineEdit()
        layout.addWidget(host_label)
        layout.addWidget(self.host_input)

        session_id_label = QLabel("Session ID:")
        self.session_id_input = QLineEdit()
        layout.addWidget(session_id_label)
        layout.addWidget(self.session_id_input)

        block_button = QPushButton("Заблокировать сессию")
        block_button.clicked.connect(self.block_session)
        layout.addWidget(block_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setVisible(False)

        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def showSelectedItems(self, success, output, return_code):
        if success:
            self.label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.label.setText("Произошла ошибка при выполнении")
        self.scroll_area.setVisible(True)
        self.label.setAlignment(Qt.AlignLeft)

    def block_session(self):
        host = self.host_input.text()
        session_id = '{"session_id":' + self.session_id_input.text() + '}'

        salt_command = f"salt -L '{host}' state.apply brine.lock_session pillar='{session_id}'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.showSelectedItems)
        self.thread.start()
