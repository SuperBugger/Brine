import json
import os
import sys
from PyQt5 import QtWidgets
from Brine import Brine


def create_initial_structure():
    if not os.path.exists('structure.json'):
        initial_data = {"items": []}
        with open('structure.json', 'w', encoding='utf-8') as file:
            json.dump(initial_data, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    create_initial_structure()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    # app.setStyleSheet(qss)

    window = Brine()
    window.setWindowTitle('Brine')
    window.setGeometry(100, 100, 600, 600)
    window.show()
    sys.exit(app.exec_())
