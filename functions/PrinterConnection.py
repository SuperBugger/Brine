from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class PrinterConnection(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        layout = QVBoxLayout()

        self.printer_name_label = QLabel("Имя принтера:")
        self.printer_name_input = QLineEdit()
        layout.addWidget(self.printer_name_label)
        layout.addWidget(self.printer_name_input)

        self.printer_path_label = QLabel(
            "Путь к принтеру (ipp://192.168.10.10/printers/printer_name или socket://192.168.10.10:9100)")
        self.printer_path_input = QLineEdit()
        layout.addWidget(self.printer_path_label)
        layout.addWidget(self.printer_path_input)

        self.connect_button = QPushButton("Подключить принтер")
        self.connect_button.clicked.connect(self.connect_printer)
        layout.addWidget(self.connect_button)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def connect_printer(self):
        printer_name = self.printer_name_input.text()
        printer_path = self.printer_path_input.text()

        if not printer_name or not printer_path:
            QMessageBox.warning(self, "Ошибка", "Имя принтера и путь к принтеру должны быть указаны.")
            return
        else:
            self.command = f"sudo lpadmin -p {printer_name} -E -v {printer_path}"

            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cmd.run '{self.command}'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.showresult)
            self.thread.start()

    def showresult(self, success, output, return_code):
        if success:
            QMessageBox.information(self, "Ок", "Изменения применены")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить команду")

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

