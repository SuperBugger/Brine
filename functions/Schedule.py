import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner
from functions.TreeListWidget import TreeListWidget


class Schedule(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self.label = QLabel("Нажмите кнопку, чтобы выполнить команду")

        scroll_area.setWidget(self.label)

        self.table = QTableWidget(7, 3)
        self.table.setHorizontalHeaderLabels(['День', 'Час', 'Минуты'])

        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days_of_week):
            item = QTableWidgetItem(day)
            self.table.setItem(i, 0, item)

        for i in range(7):
            hour_combo = QComboBox()
            hour_combo.addItems([str(j) for j in range(24)])
            minute_combo = QComboBox()

            minute_combo.addItems([f"{j:02d}" for j in range(60)])

            self.table.setCellWidget(i, 1, hour_combo)
            self.table.setCellWidget(i, 2, minute_combo)

        self.execute_button = QPushButton('Устанвоить расписание')
        self.execute_button.clicked.connect(self.execute)

        layout.addWidget(self.table)
        layout.addWidget(self.execute_button)
        layout.addWidget(scroll_area)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def showSelectedItems(self, success, output, return_code):
        if success:
            self.label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.label.setText("Произошла ошибка при выполнении")
        self.execute_button.setEnabled(True)
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
        schedule_data = {}
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        tree_list_widget = TreeListWidget()

        for i, day in enumerate(days_of_week):
            hour_combo = self.table.cellWidget(i, 1)
            minute_combo = self.table.cellWidget(i, 2)
            hour = hour_combo.currentText()
            minute = minute_combo.currentText()
            schedule_data[day.lower()] = f"{hour}:{minute}"

        schedule_json = json.dumps(schedule_data, separators=(',', ':'))

        self.execute_button.setEnabled(False)
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.timetable pillar='{schedule_json}'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.showSelectedItems)
        self.thread.start()

