from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class Keys_Subtab(QWidget):
    def __init__(self):
        super().__init__()

        self.accepted_keys = []
        self.denied_keys = []
        self.unaccepted_keys = []
        self.rejected_keys = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.setWindowTitle("Список ключей")

        self.groupboxes = []
        self.create_groupbox(layout, "Accepted Keys", self.accepted_keys, "accepted")
        self.create_groupbox(layout, "Denied Keys", self.denied_keys, "denied")
        self.create_groupbox(layout, "Unaccepted Keys", self.unaccepted_keys, "unaccepted")
        self.create_groupbox(layout, "Rejected Keys", self.rejected_keys, "rejected")

        update_button = QPushButton("Обновить ключи")
        update_button.clicked.connect(self.get_keys)
        layout.addWidget(update_button)

        accept_button = QPushButton("Принять выбранные ключи")
        accept_button.clicked.connect(self.accept_selected_keys)
        layout.addWidget(accept_button)

        del_button = QPushButton("Удалить выбранные ключи")
        del_button.clicked.connect(self.del_selected_keys)
        layout.addWidget(del_button)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        if self.text_edit.toPlainText() == "":
            self.text_edit.setVisible(False)
        layout.addWidget(self.text_edit)
        self.get_keys()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def create_groupbox(self, layout, title, keys, status):
        groupbox = QGroupBox(title)
        vbox = QVBoxLayout()

        for key in keys:
            checkbox = QCheckBox(key)
            vbox.addWidget(checkbox)

        groupbox.setLayout(vbox)
        layout.addWidget(groupbox)
        self.groupboxes.append((status, vbox))

    def update_groupbox(self, groupbox, new_keys):
        layout = groupbox.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for key in new_keys:
            checkbox = QCheckBox(key)
            layout.addWidget(checkbox)
            self.checkbox_dict[key] = checkbox

    def checkbox_changed(self):
        sender = self.sender()
        group_name = sender.objectName()
        if sender.isChecked():
            self.selected_checkboxes.append((group_name, sender.text()))
        else:
            self.selected_checkboxes.remove((group_name, sender.text()))

    def get_keys(self):
        salt_key_command = ["salt-key", "-L"]
        self.thread = CommandRunner(salt_key_command, self)
        self.thread.finished.connect(self.on_command_finished)
        self.thread.start()
        self.selected_checkboxes = []

    def on_command_finished(self, success, output, return_code):
        new_accepted_keys = []
        new_denied_keys = []
        new_unaccepted_keys = []
        new_rejected_keys = []

        lines = output.strip().split('\n')
        current_status = None

        if success:
            for line in lines:
                if line == "Accepted Keys:":
                    current_status = "accepted"
                elif line == "Denied Keys:":
                    current_status = "denied"
                elif line == "Unaccepted Keys:":
                    current_status = "unaccepted"
                elif line == "Rejected Keys:":
                    current_status = "rejected"
                else:
                    if current_status == "accepted":
                        new_accepted_keys.append(line)
                    elif current_status == "denied":
                        new_denied_keys.append(line)
                    elif current_status == "unaccepted":
                        new_unaccepted_keys.append(line)
                    elif current_status == "rejected":
                        new_rejected_keys.append(line)

            for status, vbox in self.groupboxes:
                for i in reversed(range(vbox.count())):
                    vbox.itemAt(i).widget().setParent(None)

                if status == "accepted":
                    keys = new_accepted_keys
                elif status == "denied":
                    keys = new_denied_keys
                elif status == "unaccepted":
                    keys = new_unaccepted_keys
                elif status == "rejected":
                    keys = new_rejected_keys

                for key in keys:
                    checkbox = QCheckBox(key)
                    vbox.addWidget(checkbox)

            self.accepted_keys = new_accepted_keys
            self.denied_keys = new_denied_keys
            self.unaccepted_keys = new_unaccepted_keys
            self.rejected_keys = new_rejected_keys

        else:
            QMessageBox.warning(self, "Ошибка", "Произошла ошибка при выполнении")

    def del_selected_keys(self):
        selected_keys = []

        for status, vbox in self.groupboxes:
            for i in range(vbox.count()):
                checkbox = vbox.itemAt(i).widget()
                if checkbox.isChecked():
                    selected_keys.append(checkbox.text().replace("&", ""))
                    del_command = ["salt-key -d " + checkbox.text().replace("&", "") + ' -y']
                    self.thread = CommandRunner(del_command, self)
                    self.thread.finished.connect(self.get_keys)
                    self.thread.start()
                    self.selected_checkboxes = []
        self.text_edit.setText("Удалены: " + "\n".join(selected_keys))
        self.text_edit.setVisible(True)

    def accept_selected_keys(self):
        selected_keys = []
        for status, vbox in self.groupboxes:
            for i in range(vbox.count()):
                checkbox = vbox.itemAt(i).widget()
                if checkbox.isChecked():
                    selected_keys.append(checkbox.text().replace("&", ""))
                    accept_command = ["salt-key -a " + checkbox.text().replace("&", "") + ' -y']
                    self.thread = CommandRunner(accept_command, self)
                    self.thread.finished.connect(self.get_keys)
                    self.thread.start()
                    self.selected_checkboxes = []

        self.text_edit.setText("Приняты: " + "\n".join(selected_keys))
        self.text_edit.setVisible(True)