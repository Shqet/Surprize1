from PyQt6 import QtWidgets
from UI_Options.MainForm_Options import MainFormOptions

class View(MainFormOptions):
    def setupUi(self, form):
        super().setupUi(form)
        self.form = form

    def show(self):
        self.form.show()



    def update_trajectory(self, trajectory):
        self.p_generateTrajectory.GTO.f_3DView.update_trajectory(trajectory)
        self.p_generateTrajectory.GTO.f_rearView.update_trajectory(trajectory)
        self.p_generateTrajectory.GTO.f_sideView.update_trajectory(trajectory)
        self.p_generateTrajectory.GTO.f_aboveView.update_trajectory(trajectory)

    def get_distance(self):
        return self.p_generateTrajectory.GTO.dSB_distance.value()

    def get_start_velocity(self):
        return self.p_generateTrajectory.GTO.dSB_startV.value()

    def get_angle_surface(self):
        return self.p_generateTrajectory.GTO.dSB_startHorizontalAngle.value()

    def get_angle_target(self):
        return self.p_generateTrajectory.GTO.dSB_startAboveAngle.value()

    def get_maneuverability(self):
        return self.p_generateTrajectory.GTO.dSB_maneuverability.value()

    def get_drag_coefficient(self):
        return self.p_generateTrajectory.GTO.dSB_dragCoefficient.value()

    def set_distance(self, distance):
        self.p_generateTrajectory.GTO.dSB_distance.setValue(distance)
    def set_start_velocity(self, v0):
        self.p_generateTrajectory.GTO.dSB_startV.setValue(v0)
    def set_angle_surface(self, angle_surface):
        self.p_generateTrajectory.GTO.dSB_startHorizontalAngle.setValue(angle_surface)
    def set_angle_target(self, angle_target):
        self.p_generateTrajectory.GTO.dSB_startAboveAngle.setValue(angle_target)
    def set_maneuverability(self, maneuverability):
        self.p_generateTrajectory.GTO.dSB_maneuverability.setValue(maneuverability)
    def set_drag_coefficient(self, drag_coefficient):
        self.p_generateTrajectory.GTO.dSB_dragCoefficient.setValue(drag_coefficient)
    # def get_max_steps(self):
    #     return self.dSB_maxSteps.text()

    def show_generate_trajectory_page(self):
        self.stackedWidget.setCurrentWidget(self.p_generateTrajectory)

    def show_translate_page(self):
        self.stackedWidget.setCurrentWidget(self.p_translateSignal)

    def set_opened_filename(self, filename:str):
        self.p_generateTrajectory.GTO.l_openedFileName.setText(filename)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = View()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())