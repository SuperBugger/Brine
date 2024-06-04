from TabWidget import TabWidget
from PyQt5 import QtWidgets, QtCore, QtGui

from functions.Control_Tab import Control_Tab
from functions.Initialization import Initialization
from functions.Settings_Tab import Settings_Tab
from functions.TreeEditor import TreeEditor


class Brine(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 450)

        self.tabs = TabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabs.setDocumentMode(True)

        tree = TreeEditor()
        self.initialization = Initialization()
        self.tabs.add_scrollable_tab(tree, QtGui.QIcon('computer.png'), 'Рабочие станции')

        control = Control_Tab()
        self.tabs.add_scrollable_tab(control, QtGui.QIcon('users-gear.png'), 'Управление')

        settings_tab = Settings_Tab()
        self.tabs.add_scrollable_tab(settings_tab, QtGui.QIcon('settings.png'), 'Настройка')

        self.tabs.setIconSize(QtCore.QSize(40, 40))
        self.tabs.setCurrentIndex(0)

        box = QtWidgets.QVBoxLayout(self)
        box.addWidget(self.tabs)
        box.setContentsMargins(0, 0, 0, 0)
