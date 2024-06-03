import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class scenarioWidget(QWidget):
    def __init__(self, tree_widget, scenario):
        super().__init__()

        self.tree_widget = tree_widget
        self.scenario = scenario
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self.label = QLabel("Нажмите кнопку, чтобы выполнить команду")
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scroll_area.setWidget(self.label)
        layout.addWidget(scroll_area)

        self.btn_show_selected = QPushButton('Получить информацию')
        self.btn_show_selected.clicked.connect(self.execute)
        layout.addWidget(self.btn_show_selected)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def showSelectedItems(self, success, output, return_code):
        if success:
            pattern = r"(\w+):(?:\n.+?)*?((?:stdout:\s*(.+?)(?=\n\n|\Z))|(?:Minion did not return\. \[Not connected\]))"
            matches = re.findall(pattern, output, re.DOTALL)
            output = ""
            for match in matches:
                machine_name, _, content = match
                if content.startswith('stdout:'):
                    output += f"{machine_name}:\n{content[7:].strip()}\n"
                else:
                    output += f"{machine_name}:\n{_}\n"

            self.label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.label.setText("Произошла ошибка при выполнении")
        self.btn_show_selected.setEnabled(True)
        self.label.setAlignment(Qt.AlignLeft)

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

    def execute(self):
        self.btn_show_selected.setEnabled(False)
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply {self.scenario}"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.showSelectedItems)
        self.thread.start()
