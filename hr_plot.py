import sys
import matplotlib.pyplot as plt
import ast
import numpy as np
import collections


from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import serial

class plotter():
  def __init__(self, pool):

    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Graph")
    win.resize(1000,600)
    win.setWindowTitle('Nexus plotting')

    p1 = win.addPlot(title="Nexus1")
    self.curve1 = p1.plot(pen='y')
    win.nextRow()
    p2 = win.addPlot(title="Nexus2")
    self.curve2 = p2.plot(pen='y')

    self.pool = pool

    timer = QtCore.QTimer()
    timer.timeout.connect(self.update)
    timer.start(1000)
    QtGui.QApplication.instance().exec_()

  def update(self):
    if self.pool.graph:
        self.curve1.setData(self.pool.bvp.nexus[0][0][:-1], self.pool.nexus[0][1][:-1])
        self.curve2.setData(self.pool.bvp.nexus[1][0][:-1], self.pool.nexus[1][1][:-1])

def live_plot(pool):
    plotter(pool)

