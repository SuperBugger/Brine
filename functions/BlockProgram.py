from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


# Класс BlockProgram управляет блокировкой и разблокировкой программ для пользователей
class BlockProgram(QWidget):
    # Конструктор класса, инициализирует виджет дерева
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()

        self.btn_search_repo_user = QPushButton('Вывести установленные пакеты')
        self.btn_search_repo_user.clicked.connect(self.search_repo_user)
        layout.addWidget(self.btn_search_repo_user)

        self.result_list = QListWidget()
        self.result_list.setVisible(False)
        layout.addWidget(self.result_list)

        self.user_input = QLineEdit()
        layout.addWidget(self.user_input)
        self.user_input.setVisible(False)

        self.blockprog_button = QPushButton('Заблокировать пользователю выбранные программы')
        self.blockprog_button.setVisible(False)
        self.blockprog_button.clicked.connect(self.blockProg_user)
        layout.addWidget(self.blockprog_button)

        self.unblockprog_button = QPushButton('Разблокировать пользователю выбранные программы')
        self.unblockprog_button.setVisible(False)
        self.unblockprog_button.clicked.connect(self.unblockProg_user)
        layout.addWidget(self.unblockprog_button)

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

    # Метод для поиска установленных пакетов на выбранных хостах
    def search_repo_user(self):
        self.btn_search_repo_user.setEnabled(False)
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' cmd.run_stdout 'dpkg --get-selections'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.showSelectedItems)
        self.thread.start()

    # Метод для отображения установленных пакетов
    def showSelectedItems(self, success, output, return_code):
        self.btn_search_repo_user.setEnabled(True)
        self.result_list.clear()
        if success:
            lines = output.splitlines()
            for line in lines:
                item = QListWidgetItem(line.split()[0])
                if line.endswith(":"):
                    item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                else:
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                self.result_list.addItem(item)
        else:
            self.result_list.addItem("Произошла ошибка при выполнении")
        self.result_list.setVisible(True)
        self.blockprog_button.setVisible(True)
        self.unblockprog_button.setVisible(True)
        self.user_input.setVisible(True)

    # Метод для отображения результата выполнения команды
    def show_result(self, success, output, return_code):
        if success:
            self.result_label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.result_label.setText("Произошла ошибка при выполнении")
        self.result_label.setVisible(True)
        self.scroll_area.setVisible(True)
        self.blockprog_button.setEnabled(True)
        self.unblockprog_button.setEnabled(True)

    # Метод для блокировки программ для пользователя
    def blockProg_user(self):
        self.blockprog_button.setEnabled(False)
        user_name = self.user_input.text()
        selected_items = [self.result_list.item(i).text().split(' - ')[0] for i in range(self.result_list.count()) if
                          self.result_list.item(i).checkState() == Qt.Checked]

        if selected_items and user_name:
            selected_items_string = ' '.join(selected_items)
            item = QListWidgetItem(selected_items_string)
            self.result_list.clear()
            self.result_list.addItem(item)
            commands = ' '.join([f'$(readlink -f $(which {item}))' for item in selected_items])
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cmd.run 'setfacl -m u:{user_name}:--- {commands}  &&  getfacl {commands} | grep {user_name} || echo \"Произошла ошибка\"'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
        else:
            self.result_label.setText("Выберите пакеты для установки и имя пользователя")
            self.blockprog_button.setEnabled(True)
            self.scroll_area.setVisible(True)

    # Метод для разблокировки программ для пользователя
    def unblockProg_user(self):
        user_name = self.user_input.text()
        selected_items = [self.result_list.item(i).text().split(' - ')[0] for i in range(self.result_list.count()) if
                          self.result_list.item(i).checkState() == Qt.Checked]

        if selected_items and user_name:
            selected_items_string = ' '.join(selected_items)
            item = QListWidgetItem(selected_items_string)
            self.result_list.clear()
            self.result_list.addItem(item)
            commands = ' '.join([f'$(readlink -f $(which {item}))' for item in selected_items])
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cmd.run_stdout 'setfacl -x u:{user_name} {commands} && getfacl {commands} | grep user  || echo \"Произошла ошибка\"'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
        else:
            self.result_label.setText("Выберите пакеты для установки и имя пользователя")
            self.scroll_area.setVisible(True)

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

