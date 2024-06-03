import yaml
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class ConfigChanger_Subtab(QWidget):
    def __init__(self):
        super().__init__()

        self.config_data = None

        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.group_box = QGroupBox("Конфигурация", self)
        self.group_box_layout = QVBoxLayout(self.group_box)

        self.group_box_layout.addWidget(self.create_settings_table())
        self.group_box_layout.addWidget(self.create_save_button())
        self.group_box_layout.addWidget(self.create_restart_button())

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.group_box)

        self.show()

    def show_keys_window(self):
        keys_window = KeysWindow(self)
        keys_window.exec_()

    def create_settings_table(self):
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])

        return self.table_widget

    def create_save_button(self):
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_config)

        return save_button

    def create_restart_button(self):
        self.restart_button = QPushButton("Перезапустить")
        self.restart_button.clicked.connect(self.restart_salt_master)

        return self.restart_button

    def load_config(self):
        self.file_name = '/etc/salt/master'
        with open(self.file_name, "r") as file:
            try:
                self.config_data = yaml.safe_load(file)
                self.populate_table()
            except yaml.YAMLError as e:
                QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def populate_table(self):
        if not self.config_data:
            return

        self.table_widget.clear()
        self.table_widget.setRowCount(len(self.config_data))
        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])

        for row, (key, value) in enumerate(self.config_data.items()):
            key_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(str(value))

            self.table_widget.setItem(row, 0, key_item)
            self.table_widget.setItem(row, 1, value_item)

    def save_config(self):
        if not self.config_data:
            return

        try:
            self.update_config_data()
            with open(self.file_name, "w") as file:
                yaml.dump(self.config_data, file)
            QMessageBox.information(self, "Ок", "Конфигурация была изменена")
        except yaml.YAMLError as e:
            QMessageBox.warning(self, "Ошибка сохранения", str(e))

    def restart_salt_master(self):
        self.restart_button.setEnabled(False)
        restart_salt_command = f"salt-call service.restart salt-master"
        self.thread = CommandRunner(restart_salt_command, self)
        self.thread.finished.connect(self.enable_restart_button)
        self.thread.start()

    def enable_restart_button(self):
        self.restart_button.setEnabled(True)

    def update_config_data(self):
        if not self.config_data:
            return

        for row in range(self.table_widget.rowCount()):
            key_item = self.table_widget.item(row, 0)
            value_item = self.table_widget.item(row, 1)

            if key_item is not None and value_item is not None:
                key = key_item.text()
                value = value_item.text()

                if value.isdigit():
                    value = int(value)
                elif value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False

                self.config_data[key] = value
