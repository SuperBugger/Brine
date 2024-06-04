import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner
from functions.CustomTreeWidget import CustomTreeWidget


class TreeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.tree = CustomTreeWidget(self)
        self.tree.setHeaderLabel("Компьютеры и группы")
        layout.addWidget(self.tree)

        self.btnAdd = QPushButton("Добавить группу")
        self.btnMove = QPushButton("Переместить элемент")
        self.btnDeleteGroup = QPushButton("Удалить группу")
        self.btnDeletePC = QPushButton("Удалить компьютер")
        self.btnSave = QPushButton("Сохранить")
        self.btnRefresh = QPushButton("Обновить")

        self.btnDeleteGroup.clicked.connect(self.deleteGroup)
        self.btnDeletePC.clicked.connect(self.deletePC)

        layout.addWidget(self.btnMove)
        layout.addWidget(self.btnAdd)
        layout.addWidget(self.btnDeleteGroup)
        layout.addWidget(self.btnDeletePC)
        layout.addWidget(self.btnSave)
        layout.addWidget(self.btnRefresh)

        self.loadData()

        self.btnAdd.clicked.connect(self.addElement)
        self.btnMove.clicked.connect(self.moveElement)
        self.btnRefresh.clicked.connect(self.refreshData)
        self.btnSave.clicked.connect(self.saveData)

    def clearTree(self):
        self.tree.clear()

    def loadData(self):
        if not os.path.exists('structure.json'):
            self.create_initial_structure()

        try:
            with open('structure.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.populateTree(data["items"])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка при загрузке данных", str(e))
            self.refreshData()

    def create_initial_structure(self):
        initial_data = {"items": []}
        with open('structure.json', 'w', encoding='utf-8') as file:
            json.dump(initial_data, file, indent=4, ensure_ascii=False)

    def populateTree(self, items, parent=None):
        for item in items:
            treeItem = QTreeWidgetItem([item["name"]])
            treeItem.setData(0, Qt.UserRole, item)

            if parent is None:
                self.tree.addTopLevelItem(treeItem)
            else:
                parent.addChild(treeItem)

            if "children" in item:
                self.populateTree(item["children"], treeItem)

    def addElement(self):
        selectedItems = self.tree.selectedItems()
        parentItem = None

        if selectedItems:
            selectedItem = selectedItems[0]
            selectedItemData = selectedItem.data(0, Qt.UserRole)
            if selectedItemData and 'type' in selectedItemData and selectedItemData['type'] == 'pc':
                QMessageBox.warning(self, "Невозможно добавить", "Нельзя добавить элемент в компьютер.")
                return
            else:
                parentItem = selectedItem

        self.addElementDialog(parentItem)

    def addElementDialog(self, parentItem=None):
        text, ok = QInputDialog.getText(self, 'Добавить группу', 'Введите название группы:')

        if ok and text:
            newGroup = QTreeWidgetItem([text])
            newGroup.setData(0, Qt.UserRole, {'name': text})

            if parentItem:
                parentItem.addChild(newGroup)
            else:
                self.tree.addTopLevelItem(newGroup)

    def addElementAtTopLevel(self):
        self.addElementDialog()

    def refreshData(self):
        salt_key_command = ["salt-key -l accepted"]
        self.thread = CommandRunner(salt_key_command, self)
        self.thread.finished.connect(self.on_command_finished)
        self.thread.start()

    def collect_pc_items(self, items, pc_items):
        for item in items:
            if item.get("type") == "pc":
                pc_items.add(item["name"])
            if "children" in item:
                self.collect_pc_items(item["children"], pc_items)

    def on_command_finished(self, success, output, return_code):
        salt_accepted_keys = set(line for line in output.splitlines() if line and line != "Accepted Keys:")
        try:
            with open('structure.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            pc_items = set()
            if "items" in data:
                self.collect_pc_items(data["items"], pc_items)
            missing_keys = salt_accepted_keys - pc_items
            if missing_keys:
                if not data.get("items"):
                    data["items"] = []
                data["items"].extend({"name": missing_key, "type": "pc"} for missing_key in missing_keys)
                with open('structure.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            salt_accepted_keys = output.splitlines()
            if len(salt_accepted_keys) > 1:
                result = {
                    "items": [
                        {
                            "name": "Принятые",
                            "children": [{"name": line, "type": "pc"} for line in salt_accepted_keys if
                                         line != "Accepted Keys:"],
                        }
                    ]
                }
                with open("structure.json", 'w') as file:
                    json.dump(result, file)
        self.clearTree()
        self.loadData()

    def moveElement(self):
        selectedItems = self.tree.selectedItems()
        if len(selectedItems) == 0:
            QMessageBox.warning(self, "", "Пожалуйста, выберите элемент для перемещения")
            return

        itemToMove = selectedItems[0]
        targetGroup, ok = QInputDialog.getItem(self, "Выберите группу",
                                               "Группы:", self.getGroupNames(itemToMove))
        if ok and targetGroup:
            targetGroupItem = self.findItemByName(self.tree.invisibleRootItem(), targetGroup)
            if targetGroupItem:
                parent = itemToMove.parent()
                if parent:
                    parent.removeChild(itemToMove)
                else:
                    self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(itemToMove))
                targetGroupItem.addChild(itemToMove)

    def getGroupNames(self):
        names = []
        self.collectGroupNames(self.tree.invisibleRootItem(), names)
        return names

    def collectGroupNames(self, item, names, itemToMove=None):
        for i in range(item.childCount()):
            child = item.child(i)

            if child == itemToMove:
                continue

            childData = child.data(0, Qt.UserRole)

            if childData and 'type' in childData:
                if childData['type'] == 'pc':
                    continue
            else:
                names.append(child.text(0))
                self.collectGroupNames(child, names, itemToMove)

    def getGroupNames(self, itemToMove=None):
        names = []
        self.collectGroupNames(self.tree.invisibleRootItem(), names, itemToMove)
        return names

    def findItemByName(self, item, name):
        if item.text(0) == name:
            return item
        for i in range(item.childCount()):
            foundItem = self.findItemByName(item.child(i), name)
            if foundItem:
                return foundItem
        return None

    def saveData(self):
        data = {'items': self.collectData(self.tree.invisibleRootItem())}

        try:
            with open('structure.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            QMessageBox.warning(self, "", "Данные успешно сохранены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка при сохранении данных", str(e))

    def collectData(self, item):
        children = []
        for i in range(item.childCount()):
            child = item.child(i)
            childData = child.data(0, Qt.UserRole)

            if childData:
                node = {'name': childData['name']}
                if 'type' in childData:
                    node['type'] = childData['type']
                if child.childCount() > 0:
                    node['children'] = self.collectData(child)
                children.append(node)
        return children

    def deleteGroup(self):
        selectedItems = self.tree.selectedItems()
        if not selectedItems:
            QMessageBox.warning(self, "Выберите группу", "Пожалуйста, выберите группу для удаления.")
            return

        selectedItem = selectedItems[0]
        selectedItemData = selectedItem.data(0, Qt.UserRole)

        if selectedItemData and 'type' in selectedItemData and selectedItemData['type'] == 'pc':
            QMessageBox.warning(self, "Невозможно удалить", "Выбранный элемент является компьютером, а не группой.")
            return

        while selectedItem.childCount() > 0:
            child = selectedItem.child(0)
            childData = child.data(0, Qt.UserRole)
            if childData and 'type' in childData and childData['type'] == 'pc':
                selectedItem.removeChild(child)
                self.tree.addTopLevelItem(child)

        parent = selectedItem.parent()
        if parent:
            parent.removeChild(selectedItem)
        else:
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(selectedItem))

    def deletePC(self):
        selectedItems = self.tree.selectedItems()
        if not selectedItems:
            QMessageBox.warning(self, "Выберите компьютер", "Пожалуйста, выберите компьютер для удаления.")
            return

        selectedItem = selectedItems[0]
        selectedItemData = selectedItem.data(0, Qt.UserRole)

        if 'type' in selectedItemData:
            parent = selectedItem.parent()
            if parent is None:
                index = self.tree.indexOfTopLevelItem(selectedItem)
                self.tree.takeTopLevelItem(index)
            else:
                parent.removeChild(selectedItem)
            return
        else:
            QMessageBox.warning(self, "Невозможно удалить", "Выбранный элемент является группой")
            return
