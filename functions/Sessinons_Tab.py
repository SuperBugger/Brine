from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.BlockSession import BlockSession
from functions.Getsessions import Getsessions
from functions.ScreenLock_Tab import ScreenLock_Tab
from functions.Timetable_Tab import Timetable_Tab


class Sessinons_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        BlockSessinon = BlockSession()
        Timetable = Timetable_Tab()
        listsessinon = Getsessions()
        scrinlock = ScreenLock_Tab()

        tab_widget = QTabWidget()
        tab_widget.addTab(listsessinon, "Лист сессий")
        tab_widget.addTab(BlockSessinon, "Блокировать сессию")
        tab_widget.addTab(Timetable, "Рассписание")
        tab_widget.addTab(scrinlock, "Блокировка экрана")

        layout.addWidget(tab_widget)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
