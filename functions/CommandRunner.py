import subprocess

from PyQt5.QtCore import *


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
        except subprocess.CalledProcessError:
            self.finished.emit(False, "", -1)