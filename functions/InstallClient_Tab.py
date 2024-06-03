import socket

import paramiko
from PyQt5.QtWidgets import *


class InstallClient_Tab(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.hostname_label = QLabel("Host:")
        self.hostname_input = QLineEdit("")
        self.layout.addWidget(self.hostname_label)
        self.layout.addWidget(self.hostname_input)

        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit("")
        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.port_input)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.execute_button = QPushButton("Установить")
        self.layout.addWidget(self.execute_button)
        self.execute_button.clicked.connect(self.execute_commands)

        self.connect_button = QPushButton("Подключить")
        self.layout.addWidget(self.connect_button)
        self.connect_button.clicked.connect(self.connect_commands)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

        self.setLayout(self.layout)

    def validate_input(self):
        hostname = self.hostname_input.text()
        port = self.port_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        if not hostname or not port or not username or not password:
            self.output_text.setText("Все поля должны быть заполнены.")
            return False
        try:
            port = int(port)
        except ValueError:
            self.output_text.setText("Порт должен быть числом.")
            return False
        return True

    def execute_commands(self):
        if not self.validate_input():
            return

        hostname = self.hostname_input.text()
        port = int(self.port_input.text())
        username = self.username_input.text()
        password = self.password_input.text()

        sudo_password = password

        local_ip = self.get_local_ip()

        commands = [
            f"echo '{sudo_password}' | sudo -S apt-get update",
            f"echo '{sudo_password}' | sudo -S apt-get install salt-minion -y",
            f'echo "{sudo_password}" | sudo -S sed -i "s/#master: salt/master: {local_ip} #brine/g"  /etc/salt/minion',
            f'echo "{sudo_password}" | sudo -S systemctl restart salt-minion',
            f'echo "{sudo_password}" | sudo -S salt-minion  --version'
        ]

        self.perform_ssh_commands(hostname, port, username, password, commands)

    def connect_commands(self):
        if not self.validate_input():
            return

        hostname = self.hostname_input.text()
        port = int(self.port_input.text())
        username = self.username_input.text()
        password = self.password_input.text()

        sudo_password = password

        local_ip = self.get_local_ip()

        connection_commands = [
            f'echo "{sudo_password}" | sudo -S sed -i "s/#master: salt/master: {local_ip} #brine/g"  /etc/salt/minion',
            f"echo '{sudo_password}' | sudo -S sed -i 's/\(master: \).*#brine/\\1{local_ip} #brine/' /etc/salt/minion",
            f'echo "{sudo_password}" | sudo -S systemctl restart salt-minion',
            f'echo "{sudo_password}" | sudo -S grep "brine" /etc/salt/minion'
        ]

        self.perform_ssh_commands(hostname, port, username, password, connection_commands)

    def perform_ssh_commands(self, hostname, port, username, password, commands):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname, port, username, password)
            self.output_text.clear()

            for command in commands:
                stdin, stdout, stderr = ssh.exec_command(command)
                output = stdout.read().decode()
                error = stderr.read().decode()
                if output:
                    self.output_text.append(output)
                if error:
                    self.output_text.append(error)
        except Exception as e:
            self.output_text.append(f"Ошибка при подключении или выполнении команд: {e}")
        finally:
            ssh.close()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except socket.error:
            return "Не удалось определить локальный IP-адрес."
