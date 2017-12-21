from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

import qdarkstyle

from GUI import MainWindow

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    launch = MainWindow()
    launch.show()
    sys.exit(app.exec_())
