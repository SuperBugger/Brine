from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class SetProxy(QWidget):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    def init_ui(self):
        self.http_checkbox = QCheckBox('HTTP')
        self.https_checkbox = QCheckBox('HTTPS')
        self.ftp_checkbox = QCheckBox('FTP')

        self.clear_button = QPushButton('Очистить', self)
        self.clear_button.setDisabled(True)
        self.clear_button.clicked.connect(self.clear_proxy)

        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()
        self.login_input = QLineEdit()
        self.password_input = QLineEdit()

        self.connect_button = QPushButton('Подключить', self)
        self.connect_button.clicked.connect(self.connect_proxy)

        self.scroll_area = QScrollArea()
        self.result_label = QLabel('Результат подключения будет отображен здесь.')
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.http_checkbox)
        layout.addWidget(self.https_checkbox)
        layout.addWidget(self.ftp_checkbox)
        layout.addWidget(QLabel('IP:'))
        layout.addWidget(self.ip_input)
        layout.addWidget(QLabel('Порт:'))
        layout.addWidget(self.port_input)
        layout.addWidget(QLabel('Логин:'))
        layout.addWidget(self.login_input)
        layout.addWidget(QLabel('Пароль:'))
        layout.addWidget(self.password_input)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.clear_button)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.setWindowTitle('Прокси-подключение')
        self.show()

        self.http_checkbox.stateChanged.connect(self.handle_checkbox)
        self.https_checkbox.stateChanged.connect(self.handle_checkbox)
        self.ftp_checkbox.stateChanged.connect(self.handle_checkbox)

    def connect_proxy(self):
        ip = self.ip_input.text()
        port = self.port_input.text()
        login = self.login_input.text()
        password = self.password_input.text()

        proxy_settings = f'http_proxy=http://{login}:{password}@{ip}:{port}/\\n' if self.http_checkbox.isChecked() else ''
        proxy_settings += f'https_proxy=https://{login}:{password}@{ip}:{port}/\\n' if self.https_checkbox.isChecked() else ''
        proxy_settings += f'ftp_proxy=ftp://{login}:{password}@{ip}:{port}/\\n' if self.ftp_checkbox.isChecked() else ''

        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        if hosts:
            salt_command = f"salt -L '{hosts}' cmd.run_stdout 'echo \"{proxy_settings}\" >> /etc/environment & source /etc/environment & cat /etc/environment'"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()
        else:
            self.result_label.setText("Выберите компьютер")

    def handle_checkbox(self, state):
        http_checked = self.http_checkbox.isChecked()
        https_checked = self.https_checkbox.isChecked()
        ftp_checked = self.ftp_checkbox.isChecked()

        clear_button_text = ''
        if http_checked:
            clear_button_text += 'HTTP,'
        if https_checked:
            clear_button_text += 'HTTPS,'
        if ftp_checked:
            clear_button_text += 'FTP'

        clear_button_text = clear_button_text.rstrip(',')

        self.clear_button.setText(f'Очистить {clear_button_text}')

        self.clear_button.setDisabled(not (http_checked or https_checked or ftp_checked))

    def clear_proxy(self):
        clear_command = ''
        if self.http_checkbox.isChecked():
            clear_command += 'sudo sed -i "/http_proxy/d" /etc/environment && '
        if self.https_checkbox.isChecked():
            clear_command += 'sudo sed -i "/https_proxy/d" /etc/environment && '
        if self.ftp_checkbox.isChecked():
            clear_command += 'sudo sed -i "/ftp_proxy/d" /etc/environment && '

        clear_command = clear_command.rstrip(' && ')

        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        if hosts:
            salt_command = f"salt -L '{hosts}' cmd.run_stdout '{clear_command} && echo \"Команда успешно выполнена\" || echo \"Произошла ошибка\" & cat /etc/environment'"
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

