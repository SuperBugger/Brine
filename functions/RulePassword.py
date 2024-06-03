import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class RulePassword(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        self.tableWidget = QTableWidget(5, 3)
        self.tableWidget.setHorizontalHeaderLabels(['Параметр', 'Значение', 'Описание'])

        parameters = [
            {'name': 'minlen', 'value': '',
             'description': 'Определяет минимальную длину пароля, которую пользователь должен использовать.'},
            {'name': 'minclass', 'value': '',
             'description': 'Указывает минимальное количество классов символов, которые должны присутствовать в пароле.'},
            {'name': 'minrepeat', 'value': '',
             'description': 'Устанавливает минимальное количество символов, которые могут повторяться подряд.'},
            {'name': 'maxrepeat', 'value': '',
             'description': 'Ограничивает максимальное количество раз, которое один и тот же символ может повторяться в пароле.'},
            {'name': 'difok', 'value': '',
             'description': 'Определяет минимальное количество различных символов, которые должны быть в новом пароле по сравнению с предыдущим паролем.'},
        ]

        for row, param in enumerate(parameters):
            name_item = QTableWidgetItem(param['name'])
            value_item = QComboBox()
            value_item.addItem('--')
            value_item.addItems([str(i) for i in range(1, 26)])
            desc_item = QTableWidgetItem(param['description'])

            self.tableWidget.setItem(row, 0, name_item)
            self.tableWidget.setCellWidget(row, 1, value_item)
            self.tableWidget.setItem(row, 2, desc_item)

        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectItems)

        self.print_button = QPushButton("Применить")
        self.print_button.clicked.connect(self.print_values)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        layout.addWidget(self.print_button)
        layout.addWidget(self.output_text)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def showresult(self, success, output, return_code):
        if success:
            QMessageBox.information(self, "Ок", "Изменения применены")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить команду")

    def print_values(self):
        pillar_data = {}
        for row in range(self.tableWidget.rowCount()):
            parameter = self.tableWidget.item(row, 0).text()
            value = self.tableWidget.cellWidget(row, 1).currentText()
            if value != '--':
                pillar_data[parameter] = value

        output = json.dumps(pillar_data)
        self.output_text.setPlainText(output)

        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.common-password pillar='{output}'"
        self.output_text.setPlainText(salt_command)
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.showresult)
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

