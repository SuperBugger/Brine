from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class Update(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.install_button = QPushButton('Обновить')
        self.install_button.clicked.connect(self.install_package)
        layout.addWidget(self.install_button)

        # Scroll area for result label
        self.scroll_area = QScrollArea()
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)
        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def show_result(self, success, output, return_code):
        if success:
            self.result_label.setText(f"Вывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.result_label.setText("Произошла ошибка при выполнении")
        self.result_label.setVisible(True)
        self.install_button.setEnabled(True)
        self.scroll_area.setVisible(True)

    def install_package(self):
        self.install_button.setEnabled(False)

        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        self.result_label.setText(hosts)
        salt_command = f"salt -L '{hosts}' cmd.run_stdout 'sudo -- apt-get update && sudo apt-get dist-upgrade -y'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.show_result)
        self.thread.start()

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items
