from PyQt5.QtWidgets import *


# Класс CustomTreeWidget добавляет функциональность для обработки двойного щелчка мыши
class CustomTreeWidget(QTreeWidget):
    # Конструктор класса
    def __init__(self, parent=None):
        super(CustomTreeWidget, self).__init__(parent)

    # Метод для обработки события двойного щелчка мыши
    def mouseDoubleClickEvent(self, event):
        if self.itemAt(event.pos()) is None:
            self.clearSelection()
            # Добавление элемента на верхний уровень
            self.parent().addElementAtTopLevel()
        else:
            super(CustomTreeWidget, self).mouseDoubleClickEvent(event)
