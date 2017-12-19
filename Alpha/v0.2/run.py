from GUI import MainWindow

from PyQt5.QtWidgets import QApplication

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    launch = MainWindow()
    launch.show()
    sys.exit(app.exec_())
