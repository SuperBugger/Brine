from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.BlockProgramm_Tab import BlockProgramm_Tab
from functions.BlockСonsole_Tab import BlockСonsole_Tab
from functions.Cert_Tab import Cert_Tab
from functions.ConrtolUSB_Tab import ConrtolUSB_Tab
from functions.DelPackage_Tab import DelPackage_Tab
from functions.DeleteTempFiles_Tab import DeleteTempFiles_Tab
from functions.MountNFS_Tab import MountNFS_Tab
from functions.PACGeneratorApp import PACGeneratorApp
from functions.PackageInstall_Tab import PackageInstall_Tab
from functions.Printer_Tab import Printer_Tab
from functions.Repository_Tab import Repository_Tab
from functions.RulePassword_Tab import RulePassword_Tab
from functions.Script_Tab import Script_Tab
from functions.Sessinons_Tab import Sessinons_Tab
from functions.SetImage_Tab import SetImage_Tab
from functions.SetProxy_Tab import SetProxy_Tab
from functions.Shortcut_Tab import Shortcut_Tab
from functions.Update_Tab import Update_Tab


class Control_Tab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        sub_tabs = QTabWidget()

        script = Script_Tab()
        password = RulePassword_Tab()
        usb = ConrtolUSB_Tab()
        cert = Cert_Tab()
        update = Update_Tab()
        tmp = DeleteTempFiles_Tab()
        installpack = PackageInstall_Tab()
        delpack = DelPackage_Tab()
        proxy = SetProxy_Tab()
        shortcut = Shortcut_Tab()
        image = SetImage_Tab()
        sessions = Sessinons_Tab()
        console = BlockСonsole_Tab()
        prog = BlockProgramm_Tab()
        repo = Repository_Tab()
        pac = PACGeneratorApp()
        printert = Printer_Tab()
        Mount = MountNFS_Tab()

        sub_tabs.addTab(script, "Исполнить скрипт")
        sub_tabs.addTab(password, "Правила паролей")
        sub_tabs.addTab(usb, "Контроль USB")
        sub_tabs.addTab(cert, "Копировать Сертификат")
        sub_tabs.addTab(update, "Обновление")
        sub_tabs.addTab(tmp, "Очистить временные файлы")
        sub_tabs.addTab(installpack, "Установить пакет")
        sub_tabs.addTab(delpack, "Удалить пакет")
        sub_tabs.addTab(repo, "Репозитории")
        sub_tabs.addTab(proxy, "Настрока прокси")
        sub_tabs.addTab(shortcut, "Создать ярлык")
        sub_tabs.addTab(image, "Задать обои")
        sub_tabs.addTab(sessions, "Управления сессиями")
        sub_tabs.addTab(console, "Управления консолью")
        sub_tabs.addTab(prog, "Права на программы")
        sub_tabs.addTab(pac, "PAC")
        sub_tabs.addTab(printert, "Подключение принтера")
        sub_tabs.addTab(Mount, "Подключение сетевого каталога")

        layout.addWidget(sub_tabs)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

