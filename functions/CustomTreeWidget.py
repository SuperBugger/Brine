from PyQt5.QtWidgets import *


class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(CustomTreeWidget, self).__init__(parent)

    def mouseDoubleClickEvent(self, event):
        if self.itemAt(event.pos()) is None:
            self.clearSelection()
            self.parent().addElementAtTopLevel()
        else:
            super(CustomTreeWidget, self).mouseDoubleClickEvent(event)
