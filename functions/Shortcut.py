import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class Shortcut(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.comment_edit = QLineEdit()
        self.exec_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.icon_edit = QLineEdit()

        self.type_combo = QComboBox()
        self.type_combo.addItems(['Application', 'Link', 'Dictionary'])

        form_layout.addRow('Name:', self.name_edit)
        form_layout.addRow('Comment:', self.comment_edit)
        form_layout.addRow('Exec:', self.exec_edit)
        form_layout.addRow('URL:', self.url_edit)
        form_layout.addRow('Icon:', self.icon_edit)
        form_layout.addRow('Type:', self.type_combo)

        self.path_edit = QLineEdit()
        self.path_label = QLabel('Путь до расположения ярлыка:')
        form_layout.addRow(self.path_label, self.path_edit)

        create_button = QPushButton('Создать ярлык')
        create_button.clicked.connect(self.create_shortcut)

        form_layout.addRow(create_button)

        self.scroll_area = QScrollArea()
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)

        layout.addLayout(form_layout)
        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.setWindowTitle('Создать ярлык')
        self.show()

    def create_shortcut(self):
        name = self.name_edit.text()
        comment = self.comment_edit.text()
        exec_command = self.exec_edit.text()
        url = self.url_edit.text()
        icon_path = self.icon_edit.text()
        shortcut_type = self.type_combo.currentText()
        desktop_path = self.path_edit.text().replace(' ', r'\ ')

        shortcut_path = os.path.join(desktop_path, f"{name}.desktop")

        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        if hosts:
            salt_command = f"salt -L '{hosts}' cmd.run_stdout 'echo \"[Desktop Entry]\\nName={name}\\nComment={comment}\\nExec={exec_command}\\nURL={url}\\nIcon={icon_path}\\nType={shortcut_type}\" > {shortcut_path}\ && chmod +x {shortcut_path}; ls {shortcut_path}'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
        else:
            self.result_label.setText("Выберите компьютер")
            self.scroll_area.setVisible(True)

    def show_result(self, success, output, return_code):
        if success:
            self.result_label.setText(f"Вывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.result_label.setText("Произошла ошибка при выполнении")
        self.result_label.setVisible(True)
        self.scroll_area.setVisible(True)

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

