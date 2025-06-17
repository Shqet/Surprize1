

from UI.CustomWidgets.View_pyqtgraph import ViewPyqtgraph


class AboveViewPyqtgraph(ViewPyqtgraph):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_axis_labels(x_label='X', y_label='Y')
        self.set_plot_title('Вид сверху')

    def update_trajectory(self, trajectory: list[tuple[float, float, float]]):
        new_x = []
        new_y = []
        for item in trajectory:
            new_x.append(item[0])
            new_y.append(item[1])
        self.curve.setData(new_x, new_y)
