import subprocess

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Initialization(QObject):
    finished = pyqtSignal(bool, str, int)

    def __init__(self):
        super().__init__()
        service_name = "salt-master"
        is_active = self.check_service_status(service_name)

        if not is_active:
            restart_salt_command = f"systemctl restart {service_name}"
            self.thread = self.CommandRunner(restart_salt_command, self)
            self.thread.finished.connect(self.enable_restart_button)
            self.thread.start()

    def check_service_status(self, service_name):
        try:
            command = f"systemctl is-active {service_name}"
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout.strip().lower() == "active"
        except subprocess.CalledProcessError as e:
            return False

    def enable_restart_button(self, success, result, return_code):
        if not success and "Permission denied" in result:
            self.show_permission_error_dialog()
        else:
            print(f"Успешно: {success}, Вывод: {result}, Код возврата: {return_code}")

    def show_permission_error_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Недостаточно прав для выполнения операции.")
        msg.setInformativeText("Вы можете запустить программу от имени суперпользователя (root) или использовать sudo.")
        msg.setWindowTitle("Ошибка доступа")
        msg.exec_()

    class CommandRunner(QThread):
        finished = pyqtSignal(bool, str, int)

        def __init__(self, command, parent=None):
            super().__init__(parent)
            self.command = command

        def run(self):
            try:
                process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           text=True)
                stdout, stderr = process.communicate()
                return_code = process.returncode
                self.finished.emit(True, stdout, return_code)
            except subprocess.CalledProcessError as e:
                self.finished.emit(False, str(e), e.returncode)