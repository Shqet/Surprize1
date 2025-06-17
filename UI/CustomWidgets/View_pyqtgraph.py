from abc import abstractmethod

from pyqtgraph import PlotWidget, mkPen

class ViewPyqtgraph(PlotWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        # Убираем фон (белый цвет)
        self.setBackground('w')

        # Настройка цвета осей, текста, линий
        axis_pen = mkPen(color='k')  # черный цвет
        self.getAxis('left').setPen(axis_pen)
        self.getAxis('bottom').setPen(axis_pen)
        self.getAxis('left').setTextPen(axis_pen)
        self.getAxis('bottom').setTextPen(axis_pen)

        self.showGrid(True, True, alpha=0.5)
        # Убираем контекстное меню
        self.setMenuEnabled(False)

        self.curve = self.plot(pen=mkPen(color='b', width=2))

    def set_axis_labels(self, x_label="", y_label=""):
        """Установить подписи осей X и Y."""
        self.setLabel('bottom', x_label)
        self.setLabel('left', y_label)

    def set_plot_title(self, title=""):
        """Установить заголовок графика."""
        self.setTitle(title, color='k', size='12pt')



    @abstractmethod
    def update_trajectory(self, trajectory: list[tuple[float, float, float]]):
        pass
