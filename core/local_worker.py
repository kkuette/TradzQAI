from PyQt5.QtCore import *

class Local_Worker(QThread):

    sig_step = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
