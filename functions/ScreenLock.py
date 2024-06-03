from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class ScreenLock(QWidget):
    def __init__(self, tree_widget):
        super(ScreenLock, self).__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Управление блокировкой экрана')

        self.checkbox = QCheckBox('Включить блокировку экрана', self)
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)

        self.slider_label = QLabel('Время блокировки (в минутах):', self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 360)
        self.slider.setValue(60)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(30)
        self.slider.valueChanged.connect(self.on_slider_changed)

        self.time_edit_label = QLabel('Или введите свое значение (1-360 минут):', self)
        self.time_edit = QLineEdit(self)
        self.time_edit.setValidator(QIntValidator(1, 360))
        self.time_edit.textChanged.connect(self.on_edit_changed)
        self.time_edit.setText(str(60))

        self.button = QPushButton('Отключить', self)
        self.button.clicked.connect(self.on_button_clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.slider_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.time_edit_label)
        layout.addWidget(self.time_edit)
        layout.addWidget(self.button)

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

    def showresult(self, success, output, return_code):
        if success:
            self.result_label.setText(f"Вывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.result_label.setText("Произошла ошибка при выполнении")
        self.result_label.setVisible(True)
        self.scroll_area.setVisible(True)

    def on_checkbox_changed(self, state):
        if state == Qt.Checked:
            self.button.setText('Включить')
        else:
            self.button.setText('Отключить')

    def on_slider_changed(self):
        value = self.slider.value()
        self.time_edit.setText(str(value))

    def on_edit_changed(self):
        text = self.time_edit.text()
        if text.isdigit():
            value = min(360, max(1, int(text)))
            self.slider.setValue(value)

    def on_button_clicked(self):
        checkbox_state = self.checkbox.checkState()
        time_value = int(self.time_edit.text())
        if checkbox_state == Qt.Checked:
            self.applytimeout(f"{{\"turn\": \"true\",\"time_value\": \"{time_value}\"}}")
        else:
            self.applytimeout(f"{{\"turn\": \"false\",\"time_value\": \"{time_value}\"}}")

    def applytimeout(self, pillar):
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.screenlock pillar='{pillar}'"
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

