from PyQt6 import QtWidgets
from PyQt6 import QtGui

from UI_Options.MainForm_Options import MainFormOptions

class View(MainFormOptions):
    def setupUi(self, form):
        super().setupUi(form)
        self.form = form
        self.trajectory_parameters = []
        self.trajectory_parameters.append(self.p_generateTrajectory.GTO.dSB_distance)
        self.trajectory_parameters.append(self.p_generateTrajectory.GTO.dSB_startV)
        self.trajectory_parameters.append(self.p_generateTrajectory.GTO.dSB_startHorizontalAngle)
        self.trajectory_parameters.append(self.p_generateTrajectory.GTO.dSB_startAboveAngle)
        self.trajectory_parameters.append(self.p_generateTrajectory.GTO.dSB_maneuverability)
        self.trajectory_parameters.append(self.p_generateTrajectory.GTO.dSB_dragCoefficient)
        self.trajectory_parameters.extend(self.p_newGenerateTrajectory.trajectory_parameters)



        self.show_generate_trajectory_page()




    def setup_icon(self, window_icon: QtGui.QIcon = None):
        self.form.setWindowIcon(window_icon)

    def connect_to_change_trajectory_parameters(self, slot):
        for parameter in self.trajectory_parameters:
            parameter.editingFinished.connect(slot)

    def show(self):
        self.form.show()





    def update_trajectory(self, trajectory):
        self.p_generateTrajectory.GTO.f_3DView.update_trajectory(trajectory)
        self.p_generateTrajectory.GTO.f_rearView.update_trajectory(trajectory)
        self.p_generateTrajectory.GTO.f_sideView.update_trajectory(trajectory)
        self.p_generateTrajectory.GTO.f_aboveView.update_trajectory(trajectory)
        self.p_newGenerateTrajectory.GTO.f_3DView.update_trajectory(trajectory)
        self.p_newGenerateTrajectory.GTO.f_rearView.update_trajectory(trajectory)
        self.p_newGenerateTrajectory.GTO.f_sideView.update_trajectory(trajectory)
        self.p_newGenerateTrajectory.GTO.f_aboveView.update_trajectory(trajectory)

        self.p_translateSignal.GTO.widget.update_trajectory(trajectory)

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

    def ask_open_file_path(self) -> str:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.form, "Загрузить траекторию", "", "TXT Files (*.txt)"
        )
        return file_path

    def ask_save_file_path(self) -> str:
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.form, "Сохранить траекторию", "", "TXT Files (*.txt)"
        )
        return file_path

    def show_error(self, message: str):
        QtWidgets.QMessageBox.critical(self.form, "Ошибка", message)

    def show_info(self, message: str):
        QtWidgets.QMessageBox.information(self.form, "Информация", message)

    # def get_max_steps(self):
    #     return self.dSB_maxSteps.text()

    def show_generate_trajectory_page(self):
        self.stackedWidget.setCurrentWidget(self.p_generateTrajectory)
        self.form.setWindowTitle("Генерация траектории")

    def show_generate_straight_trajectory_page(self):
        self.stackedWidget.setCurrentWidget(self.p_generateStraightTrajectory)
        self.form.setWindowTitle("Генерация прямой траектории")


    def show_translate_page(self):
        self.stackedWidget.setCurrentWidget(self.p_translateSignal)
        self.form.setWindowTitle("Трансляция")

    def set_opened_filename(self, filename:str):
        self.p_generateTrajectory.GTO.l_openedFile.setText(filename)
        # pass
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = View()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())