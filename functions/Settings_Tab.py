from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.ConfigChanger_Subtab import ConfigChanger_Subtab
from functions.InstallClient_Tab import InstallClient_Tab
from functions.Keys_Subtab import Keys_Subtab


class Settings_Tab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        sub_tabs = QTabWidget()
        ConfigChanger = ConfigChanger_Subtab()
        Keys = Keys_Subtab()
        install = InstallClient_Tab()
        sub_tabs.addTab(ConfigChanger, "Настройка")
        sub_tabs.addTab(Keys, "Работа с ключами")
        sub_tabs.addTab(install, "Установка")
        layout.addWidget(sub_tabs)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
