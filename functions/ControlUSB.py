import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


# Класс ControlUSB управляет блокировкой и разблокировкой USB-хранилищ на удаленных хостах
class ControlUSB(QWidget):
    # Конструктор класса, инициализирует интерфейс
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()

        self.block_button = QPushButton('Заблокировать USB-хранилища')
        self.block_button.clicked.connect(self.block_usb)
        layout.addWidget(self.block_button)

        self.unblock_button = QPushButton('Разблокировать USB-хранилища')
        self.unblock_button.clicked.connect(self.unblock_usb)
        layout.addWidget(self.unblock_button)

        self.result_label = QLabel()
        self.result_label.setVisible(False)
        layout.addWidget(self.result_label)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    # Метод для отображения результата выполнения команды
    def show_result(self, success, output, return_code):
        if success:
            pattern = r"^(\w+):(?:\n(?:.*?\n)+?)*?(?:\s*ID:\s*grepusbrules.*?\n.*?stdout:\n\s*(.+?)\n\n|\s*Minion did not return. \[Not connected\])"
            matches = re.findall(pattern, output, re.MULTILINE | re.DOTALL)
            output = ""
            for match in matches:
                machine_name, stdout = match
                if stdout:
                    output += f"{machine_name}:\n{stdout}\n"
                else:
                    output += f"{machine_name}:\n    Minion did not return. [Not connected]\n"

            result_text = f"{output}\n\nКод завершения: {return_code}"
        else:
            result_text = "Произошла ошибка при выполнении"
        self.result_label.setText(result_text)
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setVisible(True)
        self.block_button.setEnabled(True)
        self.unblock_button.setEnabled(True)

        self.result_label.setText(result_text)
        self.result_label.setVisible(True)

    # Метод для блокировки USB-хранилищ
    def block_usb(self):
        self.block_button.setEnabled(False)
        # Исправлено self.tree_widget.tree_widget.invisibleRootItem() на self.tree_widget.invisibleRootItem()
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.usb_rules pillar='{{\"turn\":\"1\"}}'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.show_result)
        self.thread.start()

    # Метод для разблокировки USB-хранилищ
    def unblock_usb(self):
        self.unblock_button.setEnabled(False)
        # Исправлено self.tree_widget.tree_widget.invisibleRootItem() на self.tree_widget.invisibleRootItem()
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.usb_rules pillar='{{\"turn\":\"0\"}}'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.show_result)
        self.thread.start()

    # Метод для получения выбранных элементов из дерева
    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

