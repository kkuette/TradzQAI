from environnement import Environnement

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

class WalletWindow(QWidget):

    def __init__(self, root, env):
        super(QWidget, self).__init__(root)
