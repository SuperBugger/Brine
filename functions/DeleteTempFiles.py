from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class DeleteTempFiles(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.del_tmp_users = QPushButton('Пользователей')
        self.del_tmp_users.clicked.connect(self.del_tmp_users_files)
        layout.addWidget(self.del_tmp_users)

        self.del_sys_tmp = QPushButton('Файлы системы')
        self.del_sys_tmp.clicked.connect(self.del_sys_tmp_files)
        layout.addWidget(self.del_sys_tmp)

        self.scroll_area = QScrollArea()
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)
        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def show_result(self, success, output, return_code):
        if success:
            result_text = f"Вывод команды:\n{output}\n\nКод завершения: {return_code}"
        else:
            result_text = "Произошла ошибка при выполнении"
        self.result_label.setText(result_text)
        self.result_label.setVisible(True)
        self.del_sys_tmp.setEnabled(True)
        self.del_tmp_users.setEnabled(True)
        self.scroll_area.setVisible(True)

    def del_sys_tmp_files(self):
        self.del_sys_tmp.setEnabled(False)
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.delete_system_temp_files"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.show_result)
        self.thread.start()

    def del_tmp_users_files(self):
        self.del_tmp_users.setEnabled(False)
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' state.apply brine.delete_user_temp_files pillar='{{'username': '{self.username_input.text()}'}}'"
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

