from environnement import Environnement
from candlestick import CandlestickItem

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

class ChartWindow(QWidget):

    def __init__(self, root):
        super(QWidget, self).__init__(root)
