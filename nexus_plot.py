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
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')

    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Graph")
    win.resize(1000,600)
    win.setWindowTitle('Nexus plotting')

    #eda1 = win.addPlot(title="Bvp1")
    #self.bpv_curve1 = eda1.plot(pen='r')
    bvp1 = win.addPlot(title="Eda1")
    self.eda_curve1 = bvp1.plot(pen='b')

    win.nextRow()
    #bvp2 = win.addPlot(title="Bvp2")
    #self.bpv_curve2 = bvp2.plot(pen='r')
    eda2 = win.addPlot(title="Eda2")
    self.eda_curve2 = eda2.plot(pen='b')
    self.pool = pool

    timer = QtCore.QTimer()
    timer.timeout.connect(self.update)
    timer.start(1000)
    QtGui.QApplication.instance().exec_()

  def update(self):
    if self.pool.plotting:
        t0 = self.pool.nexus.bvp[0][0][0]
        #self.bpv_curve1.setData(self.pool.nexus.bvp[0][0][:-1] - t0, self.pool.nexus.bvp[0][1][:-1])
        #self.bpv_curve2.setData(self.pool.nexus.bvp[1][0][:-1] - t0, self.pool.nexus.bvp[1][1][:-1])

        self.eda_curve1.setData(self.pool.nexus.eda[0][0][:-1] - t0, self.pool.nexus.eda[0][1][:-1])
        self.eda_curve2.setData(self.pool.nexus.eda[1][0][:-1] - t0, self.pool.nexus.eda[1][1][:-1])

def live_plot(pool):
    plotter(pool)

