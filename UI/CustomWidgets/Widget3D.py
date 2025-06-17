import numpy as np
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from pyqtgraph.opengl import GLViewWidget, GLLinePlotItem, GLGridItem
import pyqtgraph.opengl as gl


def rollingUp(value:float):
    if value == 0:
        return 0
    sign = 1 if value > 0 else -1
    x = abs(value)
    import math
    power = int(math.floor(math.log10(x)))
    rounded = round(x / 10 ** power) * 10 ** power
    return sign * rounded

class Widget3D(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid_step = 10000
        grid_range = 100000
        self.grid_step = grid_step
        self.grid_range = grid_range

        # Основной OpenGL виджет
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=grid_range * 1.2)
        self.view.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        # Добавим layout, чтобы встроить виджет GLViewWidget внутрь
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.plot_item = gl.GLLinePlotItem()
        self.view.addItem(self.plot_item)
        self.label_items = []

        self._init_grid()


    def _init_grid(self):
        # Сетка по X, Y, Z
        for axis in ['x', 'y', 'z']:
            grid = gl.GLGridItem()
            grid.setSpacing(self.grid_step, self.grid_step)
            grid.setSize(self.grid_range * 2, self.grid_range * 2)
            if axis == 'x':
                grid.rotate(90, 0, 1, 0)
            elif axis == 'y':
                grid.rotate(90, 1, 0, 0)
            self.view.addItem(grid)

    def set_grid_params(self, grid_step=None, grid_range=None):
        if grid_step is not None:
            self.grid_step = grid_step
        if grid_range is not None:
            self.grid_range = grid_range

        for item in self.view.items[:]:
            if isinstance(item, (gl.GLGridItem, gl.GLTextItem)):
                self.view.removeItem(item)

        self.label_items.clear()
        self._init_grid()


    def update_trajectory(self, trajectory: list[tuple[float, float, float]]):
        # if self.plot_item:
        #     self.view.removeItem(self.plot_item)
        distance = abs(trajectory[-1][0]-trajectory[0][0])
        step = rollingUp(distance//10)
        self.set_grid_params(step, step*11)
        # print(step)
        self.view.setCameraPosition(distance=distance*3)


        trajectory = np.array(trajectory, dtype=np.float32)
        self.plot_item.setData(pos=trajectory, color=QColor(255, 0, 0), width=2)
        # pts = np.vstack([x, y, z]).T
        # self.plot_item = gl.GLLinePlotItem(pos=pts, color=color, width=2.0, antialias=True)
        # self.view.addItem(self.plot_item)
        #
    # def update_trajectory(self, trajectory: list[tuple[float, float, float]]):
    #     # print(trajectory)
    #     trajectory = np.array(trajectory, dtype=np.float32)
    #     self.line.setData(pos=trajectory, color=QColor(255, 0, 0), width=2)
    #     # self.line.setData(pos = )
    #     pass