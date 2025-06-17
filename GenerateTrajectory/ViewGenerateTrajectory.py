from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal

from UI.GenerateTrajectory import Ui_Form


class ViewGenerateTrajectory(Ui_Form):

    def __init__(self):
        self.form = QtWidgets.QWidget()
        self.setupUi(self.form)

    def show(self):
        self.form.show()



    def update_trajectory(self, trajectory):
        self.f_3DView.update_trajectory(trajectory)
        self.f_rearView.update_trajectory(trajectory)
        self.f_sideView.update_trajectory(trajectory)
        self.f_aboveView.update_trajectory(trajectory)

    def get_distance(self):
        return self.dSB_distance.value()

    def get_start_velocity(self):
        return self.dSB_startV.value()

    def get_angle_surface(self):
        return self.dSB_startHorizontalAngle.value()

    def get_angle_target(self):
        return self.dSB_startAboveAngle.value()

    def get_maneuverability(self):
        return self.dSB_maneuverability.value()

    def get_drag_coefficient(self):
        return self.dSB_dragCoefficient.value()

    # def get_max_steps(self):
    #     return self.dSB_maxSteps.text()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = ViewGenerateTrajectory()

    Form.show()
    sys.exit(app.exec())