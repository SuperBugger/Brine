from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class MountNFSWidget(QWidget):
    def __init__(self, tree_widget):
        super().__init__()

        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        self.source_label = QLabel('Источник: (server:/mnt)')
        self.source_edit = QLineEdit(self)

        self.destination_label = QLabel('Назначение: (/mnt/)')
        self.destination_edit = QLineEdit(self)

        self.read_only_checkbox = QCheckBox('Только для чтения', self)

        self.mount_button = QPushButton('Смонтировать', self)
        self.mount_button.clicked.connect(self.show_mount_command)

        layout = QVBoxLayout()
        layout.addWidget(self.source_label)
        layout.addWidget(self.source_edit)
        layout.addWidget(self.destination_label)
        layout.addWidget(self.destination_edit)
        layout.addWidget(self.read_only_checkbox)
        layout.addWidget(self.mount_button)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def show_mount_command(self):
        source = self.source_edit.text()
        destination = self.destination_edit.text()
        read_only = 'ro' if self.read_only_checkbox.isChecked() else ''

        mount_command = "sudo mount -t nfs -v"
        if read_only:
            mount_command += f" -o {read_only}"
        mount_command += f" {source} {destination}"

        self.connect(mount_command)

    def connect(self, command):
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        if hosts:
            salt_command = f"salt -L '{hosts}' cmd.run '{command}'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
        else:
            QMessageBox.warning(self, "Ошибка", "Имя компьютеры и путь должны быть указаны.")
            return

    def show_result(self, success, output, return_code):
        if success:
            QMessageBox.warning(self, "Ошибка", output)
        else:
            QMessageBox.warning(self, "Ошибка", "Произошла ошибка при выполнении")

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

