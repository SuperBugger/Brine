from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class Repository_Disconnect(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tree_widget = self.tree_widget
        self.get_button = QPushButton('Получить репозитории')
        self.get_button.clicked.connect(self.get_repo_list)
        layout.addWidget(self.get_button)

        self.result_list = QListWidget()
        self.result_list.setVisible(False)
        layout.addWidget(self.result_list)

        self.del_button = QPushButton('Удалить выбранные')
        self.del_button.setVisible(False)
        self.del_button.clicked.connect(self.del_repo)

        layout.addWidget(self.del_button)
        layout.addWidget(self.tree_widget)

        self.scroll_area = QScrollArea()
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)

        layout.addWidget(self.scroll_area)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def get_repo_list(self):
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        if hosts:
            self.get_button.setEnabled(False)
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cmd.run_stdout 'echo \"/etc/apt/sources.list:\" && grep -v '^#' /etc/apt/sources.list && echo \"\" && for file in /etc/apt/sources.list.d/*; do echo \"$file:\" && grep -v '^#' \"$file\" && echo \"\"; done'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.showSelectedItems)
            self.thread.start()
        else:
            self.result_list.clear()
            self.result_list.addItem("Выберите компьютер.")
            self.result_list.setVisible(True)
            self.del_button.setVisible(True)

    def showSelectedItems(self, success, output, return_code):
        self.get_button.setEnabled(True)
        self.result_list.clear()
        if success:
            lines = output.splitlines()
            for line in lines:
                if line.strip():
                    item = QListWidgetItem(line)
                    if line.endswith(":"):
                        item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                    else:
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                        item.setCheckState(Qt.Unchecked)
                    self.result_list.addItem(item)
        else:
            self.result_list.addItem("Произошла ошибка при выполнении")
        self.result_list.setVisible(True)
        self.del_button.setVisible(True)

    def showresult(self, success, output, return_code):
        self.label.setVisible(True)
        if success:
            self.label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.label.setText("Произошла ошибка при выполнении")
        self.label.setAlignment(Qt.AlignLeft)
        self.scroll_area.setVisible(True)
        self.del_button.setEnabled(True)

    def del_repo(self):
        self.del_button.setEnabled(False)
        selected_items = ["{}".format(self.result_list.item(i).text().split(' - ')[0])
                          for i in range(self.result_list.count())
                          if self.result_list.item(i).checkState() == Qt.Checked]

        if selected_items:
            repos = [s.strip() for s in selected_items]
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            repos_quoted = [f'"{repo}"' for repo in repos]
            repos = ', '.join(repos_quoted)
            salt_command = f"salt -L '{hosts}' state.apply brine.repo pillar='{{\"lines_to_remove\": [{repos}]}}'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.showresult)
            self.thread.start()

            self.result_list.clear()
            self.result_list.addItem("Команда на удаление репозиториев отправлена.")
        else:
            self.result_list.addItem("Не выбраны репозитории для удаления.")
            self.del_button.setEnabled(True)

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items
