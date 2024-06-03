import json
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner
from functions.CustomHeader import CustomHeader


class TreeListWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.tree_widget = QTreeWidget()
        custom_header = CustomHeader(Qt.Horizontal, self, self.tree_widget)
        self.tree_widget.setHeader(custom_header)
        layout.addWidget(self.tree_widget)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.tree_widget.setHeaderLabels(["Компьютеры"])

        self.get_structure()
        self.updateWindowSize()

        self.tree_widget.itemClicked.connect(self.handleItemClick)
        self.tree_widget.itemChanged.connect(self.handleItemChanged)

        self.tree_widget.itemExpanded.connect(self.updateWindowSize)
        self.tree_widget.itemCollapsed.connect(self.updateWindowSize)

        self.selected_items = []

    def get_structure(self):
        self.tree_widget.clear()
        if os.path.exists('structure.json'):
            with open('structure.json', 'r') as json_file:
                data = json.load(json_file)
                self.createTreeFromData(data['items'], self.tree_widget)
        else:
            self.crate_structure()

    def crate_structure(self):
        salt_key_command = ["salt-key -l accepted"]
        self.thread = CommandRunner(salt_key_command, self)
        self.thread.finished.connect(self.on_command_finished)
        self.thread.start()

    def on_command_finished(self, success, output, return_code):
        lines = output.splitlines()
        if len(lines) > 1:
            result = {
                "items": [
                    {
                        "name": "Принятые",
                        "children": [{"name": line, "type": "pc"} for line in lines if line != "Accepted Keys:"],
                    }
                ]
            }
            with open("structure.json", 'w') as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
            self.get_structure()

    def createTreeFromData(self, data, parent_item):
        for item_data in data:
            item = QTreeWidgetItem(parent_item, [item_data['name']])
            if 'children' in item_data:
                self.createTreeFromData(item_data['children'], item)
            item.setCheckState(0, Qt.Unchecked)

    def handleItem(self, item, column):
        self.ChangeAllParentsItems(item)
        self.ChangeAllChildItems(item)

    def handleItemClick(self, item, column):
        if hasattr(self, 'item_changed') and self.item_changed:
            self.handleItem(item, column)
            self.item_changed = False

    def handleItemChanged(self, item, column):
        self.item_changed = True

    def ChangeAllParentsItems(self, item):
        parent_item = item.parent()
        while parent_item is not None:
            childCount = parent_item.childCount()
            childCheckedCount = 0
            for i in range(childCount):
                child_item = parent_item.child(i)
                if child_item.checkState(0) == Qt.Checked:
                    childCheckedCount += 1
                    parent_item.setCheckState(0, Qt.Checked)
                else:
                    parent_item.setCheckState(0, Qt.Checked)

            if childCount == childCheckedCount:
                parent_item.setCheckState(0, Qt.Checked)
            elif childCheckedCount > 0:
                parent_item.setCheckState(0, Qt.PartiallyChecked)
            else:
                parent_item.setCheckState(0, Qt.Unchecked)
            parent_item = parent_item.parent()

    def ChangeAllChildItems(self, parent_item):
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            child_item.setCheckState(0, parent_item.checkState(0))
            if child_item.childCount() > 0:
                self.ChangeAllChildItems(child_item)

    def updateWindowSize(self):
        num_visible_rows = self.getVisibleRowCount()
        new_height = 50 + num_visible_rows * 20
        self.setFixedHeight(new_height)

    def getVisibleRowCount(self):
        count = 1
        for i in range(self.tree_widget.topLevelItemCount()):
            top_level_item = self.tree_widget.topLevelItem(i)
            count += 1  # Count the top-level item itself
            if top_level_item.isExpanded():
                count += top_level_item.childCount()
        return count
