import subprocess

from PyQt5.QtCore import *


# Класс CommandRunner выполняет команду в отдельном потоке
class CommandRunner(QThread):
    # Сигнал, который будет посылаться после завершения команды
    finished = pyqtSignal(bool, str, int)

    # Конструктор класса, задает команду для выполнения
    def __init__(self, command, parent=None):
        super().__init__(parent)
        self.command = command

    # Метод, который выполняется в отдельном потоке
    def run(self):
        try:
            # Запуск команды в новом процессе
            process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)
            # Ожидание завершения процесса и получение результатов
            stdout, stderr = process.communicate()
            # Получение кода завершения процесса
            return_code = process.returncode
            # Посылка сигнала о завершении команды
            self.finished.emit(True, stdout, return_code)
        except Exception as e:  # Oтлавливаем все возможные ошибки
            # В случае ошибки посылаем сигнал с ошибкой и её описанием
            self.finished.emit(False, str(e), -1)  # Исправлено: передаем описание ошибки
