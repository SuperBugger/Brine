from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class BlockConsole(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Управление терминалом')

        self.username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()

        self.block_button = QPushButton('Заблокировать терминал')
        self.block_button.clicked.connect(self.block_terminal)

        self.unblock_button = QPushButton('Разблокировать терминал')
        self.unblock_button.clicked.connect(self.unblock_terminal)

        self.scroll_area = QScrollArea()
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.block_button)
        layout.addWidget(self.unblock_button)
        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def block_terminal(self):
        self.block_button.setEnabled(False)
        self.toggle_shell('/usr/sbin/nologin')

    def unblock_terminal(self):
        self.unblock_button.setEnabled(False)
        self.toggle_shell('/bin/bash')

    def toggle_shell(self, new_shell):
        user_name = self.username_input.text()
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        if hosts and user_name:
            salt_command = f"salt -L '{hosts}' cmd.run_stdout 'sudo usermod -s {new_shell} {user_name} && echo \"Команда успешно выполнена\" || echo \"Произошла ошибка\"'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
        else:
            self.result_label.setText("Выберите компьютер и имя пользователя")

    def show_result(self, success, output, return_code):
        if success:
            self.result_label.setText(f"Вывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.result_label.setText("Произошла ошибка при выполнении")
        self.result_label.setVisible(True)
        self.scroll_area.setVisible(True)
        self.block_button.setEnabled(True)
        self.unblock_button.setEnabled(True)

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

