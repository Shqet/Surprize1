

from UI.CustomWidgets.View_pyqtgraph import ViewPyqtgraph


class RearViewPyqtgraph(ViewPyqtgraph):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_axis_labels(x_label='Y', y_label='Z')
        self.set_plot_title('Вид сзади')

    def update_trajectory(self, trajectory: list[tuple[float, float, float]]):
        new_y = []
        new_z = []
        for item in trajectory:
            new_y.append(item[1])
            new_z.append(item[2])
        self.curve.setData(new_y, new_z)
