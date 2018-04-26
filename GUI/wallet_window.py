from environnement import Environnement

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

from .candlestick import CandlestickItem

class WalletWindow(QWidget):

    def __init__(self, root, env):
        super(QWidget, self).__init__(root)
        GB = QGridLayout(self)
        self.init_chart()
        GB.addWidget(self._chart, 0, 0)

    def init_chart(self):
        self.candleitem = CandlestickItem()
        self._chart = pg.PlotWidget()
        self._chart.addItem(self.candleitem)

    def Update_chart(self, env):
        if len(env.lst_data_full) > 1:
            self._chart.clear()
            self._chart.addItem(self.candleitem)
            self.candleitem.addData(env.lst_data_full)
            self.candleitem.generatePicture()
            self._chart.autoRange()
