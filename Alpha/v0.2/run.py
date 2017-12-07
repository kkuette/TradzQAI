from GUI.main_window import *
from tools.utils import *

from PyQt5.QtWidgets import QApplication

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    launch = MainWindow()
    launch.show()
    sys.exit(app.exec_())
    #show()
