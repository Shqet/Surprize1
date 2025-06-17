

from UI.CustomWidgets.View_pyqtgraph import ViewPyqtgraph


class SideViewPyqtgraph(ViewPyqtgraph):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_axis_labels(x_label='X', y_label='Z')
        self.set_plot_title('Вид с боку')

    def update_trajectory(self, trajectory: list[tuple[float, float, float]]):
        new_x = []
        new_z = []
        for item in trajectory:
            new_x.append(item[0])
            new_z.append(item[2])
        self.curve.setData(new_x, new_z)
