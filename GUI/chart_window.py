from environnement import Environnement
from candlestick import CandlestickItem

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

class Chart_Window(QWidget):

    def __init__(self):
        super(QWidget, self). __init__()
        self.candlestick = CandlestickItem()

    def update_chart(self, env) :
        self.candlestick.setData()
