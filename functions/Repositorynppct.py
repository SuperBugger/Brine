from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner
from functions.LoginDialog import LoginDialog


class Repositorynppct(QWidget):
    def __init__(self, tree_widget, label, scroll_area):
        super(Repositorynppct, self).__init__()
        self.tree_widget = tree_widget
        self.label = QLabel("Подключить репозиторий dl.nppct.ru")
        self.connect_button = QPushButton("Подключить")
        self.connect_button.clicked.connect(self.show_login_dialog)

        self.connect_devel_button = QPushButton("Подключить с devel")
        self.connect_devel_button.clicked.connect(self.show_login_dialog_with_devel)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.label)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.connect_devel_button)
        self.setLayout(layout)

    def show_login_dialog_with_devel(self):
        self.show_login_dialog(with_devel=True)

    def show_login_dialog(self, with_devel=None):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username = dialog.username_edit.text()
            password = dialog.password_edit.text()
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            if with_devel == True:
                salt_command = f"salt -L '{hosts}' state.apply brine.onyx_repo pillar='{{\"login\":\"{username}\", \"password\":\"{password}\", \"with_devel\":\"{with_devel}\"}}'"
            else:
                salt_command = f"salt -L '{hosts}' state.apply brine.onyx_repo pillar='{{\"login\":\"{username}\", \"password\":\"{password}\"}}'"
            print(salt_command)
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
        self.text_edit.clear()

    def showresult(self, success, output, return_code):
        self.label.setVisible(True)
        if success:
            self.label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.label.setText("Произошла ошибка при выполнении")
        self.label.setAlignment(Qt.AlignLeft)
        self.scroll_area.setVisible(True)
