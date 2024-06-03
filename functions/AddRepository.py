from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


class AddRepository(QWidget):
    def __init__(self, text_edit, add_button, tree_widget, label, scroll_area):
        super(AddRepository, self).__init__()
        self.text_edit = text_edit
        self.add_button = add_button
        self.tree_widget = tree_widget
        self.label = label
        self.scroll_area = scroll_area

    def enable_button(self):
        self.add_button.setEnabled(bool(self.text_edit.toPlainText().strip()))

    def print_text(self):
        hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
        salt_command = f"salt -L '{hosts}' cmd.run_stdout 'echo \"{self.text_edit.toPlainText()}\" >> /etc/apt/sources.list && cat /etc/apt/sources.list'"
        self.thread = CommandRunner(salt_command, self)
        self.thread.finished.connect(self.showresult)
        self.thread.start()

    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items
        self.text_edit.clear()

    def showresult(self, success, output, return_code):
        self.label.setVisible(True)
        if success:
            self.label.setText(
                f"Команда выполнена успешно.\n\nВывод команды:\n{output}\n\nКод завершения: {return_code}")
        else:
            self.label.setText("Произошла ошибка при выполнении")
        self.label.setAlignment(Qt.AlignLeft)
        self.scroll_area.setVisible(True)
