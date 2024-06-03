import sys

from PyQt5 import QtWidgets

from Brine import Brine

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    # app.setStyleSheet(qss)

    window = Brine()
    window.setWindowTitle('Brine')
    window.setGeometry(100, 100, 600, 600)
    window.show()
    sys.exit(app.exec_())
