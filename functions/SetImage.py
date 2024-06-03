import os
import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class SetImage(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Выберите изображение:")
        layout.addWidget(self.label)

        self.image_button = QPushButton("Выбрать файл")
        self.image_button.clicked.connect(self.select_image)
        layout.addWidget(self.image_button)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        layout.addWidget(self.username_input)

        self.copy_button = QPushButton("Установить обои")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_image)
        layout.addWidget(self.copy_button)

        self.image_path = None

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)

        self.scroll_area.setWidget(self.result_label)
        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
        self.scroll_area.setVisible(False)

    def show_result(self, success, output, return_code):
        if success:
            result_text = f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}"
        else:
            result_text = "Произошла ошибка при выполнении"
        os.remove(self.destination_path)
        self.result_label.setText(result_text)
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setVisible(True)
        self.scroll_area.setVisible(True)
        self.copy_button.setEnabled(True)

    def select_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                         "Picture Files (*.png *.jpeg *jpg);;All Files (*)",
                                                         options=options)

        if self.image_path:
            self.copy_button.setEnabled(True)
            self.label.setText(f"Выбранный файл: {self.image_path}")
        else:
            self.copy_button.setEnabled(False)
            self.label.setText("Файл не выбран")

    def copy_image(self):
        if self.image_path:
            image_filename = os.path.basename(self.image_path)
            saltstack_path = '/srv/salt/'
            username = self.username_input.text()

            self.destination_path = os.path.join(saltstack_path, image_filename)
            shutil.copy(self.image_path, self.destination_path)

            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' state.apply brine.pic pillar='{{'pic_filename': '{image_filename}', 'username': '{username}'}}'"
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

