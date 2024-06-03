from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class PackageInstal(QWidget):
    def __init__(self, tree_widget):
        super().__init__()

        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.package_input = QLineEdit()
        layout.addWidget(self.package_input)

        self.btn_search_repo_package = QPushButton('Поиск пакета')
        self.btn_search_repo_package.clicked.connect(self.search_repo_package)
        layout.addWidget(self.btn_search_repo_package)

        self.result_list = QListWidget()
        self.result_list.setVisible(False)
        layout.addWidget(self.result_list)

        self.install_button = QPushButton('Установить пакет')
        self.install_button.setVisible(False)
        self.install_button.clicked.connect(self.install_package)
        layout.addWidget(self.install_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)

        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setVisible(False)

        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def search_repo_package(self):
        package_name = self.package_input.text()
        if package_name:
            self.btn_search_repo_package.setEnabled(False)
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cmd.run_stdout 'apt-cache search -- {package_name}'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.showSelectedItems)
            self.thread.start()
        else:
            self.result_list.clear()
            self.result_list.addItem("Введите имя пакета для поиска.")
            self.result_list.setVisible(True)
            self.install_button.setVisible(True)

    def showSelectedItems(self, success, output, return_code):
        self.btn_search_repo_package.setEnabled(True)
        self.result_list.clear()
        if success:
            lines = output.splitlines()
            for line in lines:
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
        self.install_button.setVisible(True)

    def showInstall(self, success, output, return_code):
        if success:
            self.result_label.setText(f"Вывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.result_label.setText("Произошла ошибка при выполнении")
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setVisible(True)
        self.scroll_area.setVisible(True)
        self.install_button.setEnabled(True)

    def install_package(self):
        self.install_button.setEnabled(False)
        selected_items = [self.result_list.item(i).text().split(' - ')[0] for i in range(self.result_list.count()) if
                          self.result_list.item(i).checkState() == Qt.Checked]
        if selected_items:
            selected_items_string = ' '.join(selected_items)
            item = QListWidgetItem(selected_items_string)
            self.result_list.clear()
            self.result_list.addItem(item)
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' state.apply brine.check_sources_list pillar='{{\"packages\": \"{selected_items_string}\"}}'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.showInstall)
            self.thread.start()
        else:
            self.result_list.clear()
            self.result_list.addItem("Выберите пакеты для установки")
            self.install_button.setEnabled(True)

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items
