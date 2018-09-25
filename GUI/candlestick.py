import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui

import math

# The only required methods are paint() and boundingRect()
class CandlestickItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.picture = QtGui.QPicture()

    def addData(self, data):
        self.data = data # data must have fields: time, open, close, min, max, action

    def generatePicture(self):
    # pre-computing a QPicture object allows paint() to run much more quickly,
    # rather than re-drawing the shapes every time.
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max, action) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if action > 0:
                p.setBrush(pg.mkBrush('g'))
                p.drawPolygon(self.createPoly(3, 0.4, 90, t, min - 10, action))
            elif action < 0:
                p.setBrush(pg.mkBrush('r'))
                p.drawPolygon(self.createPoly(3, 0.4, -90, t, max + 10, action))
            if open > close:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QtCore.QRectF(t-w, open, w*2, close-open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())

    def createPoly(self, n, r, s, xx, yy, act):
        polygon = QtGui.QPolygonF()
        w = 360/n                                                       # angle per step
        for i in range(n):                                              # add the points of polygon
            t = w*i + s
            y = r*math.sin(math.radians(t))
            x = r*math.cos(math.radians(t))
            if i == 0:
                if act > 0:
                    polygon.append(QtCore.QPointF(xx +x, 2 + (yy + y)))
                elif act < 0:
                    polygon.append(QtCore.QPointF(xx +x, (yy + y) - 2))
            else:
                polygon.append(QtCore.QPointF(xx +x, yy + y))

        return polygon
