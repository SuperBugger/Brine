import os
import re
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


# Класс BashScriptExecutor отвечает за загрузку и выполнение bash-скриптов через GUI
class BashScriptExecutor(QWidget):
    # Конструктор класса, инициализирует виджет дерева
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()

        self.btn_load_script = QPushButton('Загрузить скрипт')
        self.btn_load_script.clicked.connect(self.load_script)
        layout.addWidget(self.btn_load_script)

        self.script_label = QLabel()
        layout.addWidget(self.script_label)

        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setVisible(False)
        layout.addWidget(self.scroll_area)

        self.execute_button = QPushButton('Выполнить скрипт')
        self.execute_button.clicked.connect(self.execute_script)
        self.execute_button.setVisible(False)
        layout.addWidget(self.execute_button)

        layout.setAlignment(Qt.AlignTop)
        layout.addStretch()
        self.setLayout(layout)

    # Метод для отображения результата выполнения команды
    def show_result(self, success, output, return_code):
        if success:
            # Регулярное выражение для извлечения нужных данных из вывода команды
            pattern = (r"(\w+):\s*(?:-{10}\s*pid:.*?stdout:\s*(______\s*.*?______)|Minion did not return. \[Not "
                       r"connected\])")
            matches = re.findall(pattern, output, re.DOTALL)
            output = ""
            for name, stdout in matches:
                if stdout:
                    output += f"{name}:\n{stdout}\n"
                else:
                    output += f"{name}:\n    Minion did not return. [Not connected]\n"

            result_text = f"{output}\n\nКод завершения: {return_code}"
        else:
            result_text = "Произошла ошибка при выполнении"
        self.script_label.setText(f"{self.script_filename}  результат:")
        os.remove(self.destination_path)
        self.result_label.setText(result_text)
        self.result_label.setAlignment(Qt.AlignLeft)
        self.scroll_area.setVisible(True)
        self.execute_button.setEnabled(True)

        # Исправлено дублирование
        self.adjust_scroll_area_height()

    # Метод для автоматической настройки высоты области прокрутки
    def adjust_scroll_area_height(self):
        font_metrics = QFontMetrics(self.result_label.font())
        width = self.result_label.width()
        rect = font_metrics.boundingRect(0, 0, width, 0, Qt.TextWordWrap, self.result_label.text())

        self.scroll_area.setMinimumHeight(rect.height())
        self.scroll_area.setMaximumHeight(rect.height())

    # Метод для загрузки скрипта с файловой системы
    def load_script(self):
        options = QFileDialog.Options()
        script_file, _ = QFileDialog.getOpenFileName(self, 'Выберите файл скрипта', '',
                                                     'Bash Scripts (*.sh);;All Files (*)', options=options)
        if script_file:
            self.script_path = script_file

            self.script_label.setText(f"Загружен скрипт: {os.path.basename(self.script_path)}")
            self.execute_button.setVisible(True)

    # Метод для выполнения загруженного скрипта
    def execute_script(self):
        if self.script_path:
            self.script_filename = os.path.basename(self.script_path)
            saltstack_path = '/srv/salt/'

            self.destination_path = os.path.join(saltstack_path, self.script_filename)
            shutil.copy(self.script_path, self.destination_path)

            # Исправлено self.tree_widget.tree_widget.invisibleRootItem() на self.tree_widget.invisibleRootItem()
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cmd.script salt://{self.script_filename}"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
            self.script_label.setText(f"Скрипт {self.script_filename} выполняется")
        else:
            self.script_label.setText("Выберите файл скрипта для выполнения.")

    # Метод для получения выбранных элементов из дерева
    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

