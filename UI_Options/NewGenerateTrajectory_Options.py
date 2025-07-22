from PyQt6 import QtWidgets

from UI.NewGenerateTrajectory import Ui_Form


class NewGenerateTrajectoryOptions(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.GTO = Ui_Form()
        self.GTO.setupUi(self)
        self.trajectory_parameters = []
        self.trajectory_parameters.append(self.GTO.dSB_coordX)
        self.trajectory_parameters.append(self.GTO.dSB_coordY)
        self.trajectory_parameters.append(self.GTO.dSB_coordZ)
        self.trajectory_parameters.append(self.GTO.dSB_coordX1)
        self.trajectory_parameters.append(self.GTO.dSB_coordY1)
        self.trajectory_parameters.append(self.GTO.dSB_coordZ1)
        self.trajectory_parameters.append(self.GTO.dSB_startV)
        self.trajectory_parameters.append(self.GTO.dSB_startHorizontalAngle)
        self.trajectory_parameters.append(self.GTO.dSB_startAboveAngle)
        self.trajectory_parameters.append(self.GTO.dSB_weight)
        self.trajectory_parameters.append(self.GTO.dSB_frontalCrossSectionalArea)
        self.trajectory_parameters.append(self.GTO.dSB_resistanceCoefficient)
        self.trajectory_parameters.append(self.GTO.dSB_airDensity)
        self.trajectory_parameters.append(self.GTO.dSB_precessionControlCoefficient)
        self.trajectory_parameters.append(self.GTO.dSB_startingSpeedHF)
        self.trajectory_parameters.append(self.GTO.dSB_finishedSpeedHF)

    def get_start_point(self):
        return self.GTO.dSB_coordX.value(), self.GTO.dSB_coordY.value(), self.GTO.dSB_coordZ.value()

    def get_end_point(self):
        return self.GTO.dSB_coordX1.value(), self.GTO.dSB_coordY1.value(), self.GTO.dSB_coordZ1.value()

    def get_start_velocity(self):
        return self.GTO.dSB_startV.value()

    def get_start_horizontal_angle(self):
        return self.GTO.dSB_startHorizontalAngle.value()

    def get_start_above_angle(self):
        return self.GTO.dSB_startAboveAngle.value()


    def get_weight(self):
        return self.GTO.dSB_weight.value()

    def get_frontal_cross_sectional_area(self):
        return self.GTO.dSB_frontalCrossSectionalArea.value()

    def get_resistance_coefficient(self):
        return self.GTO.dSB_resistanceCoefficient.value()

    def get_air_density(self):
        return self.GTO.dSB_airDensity.value()

    def get_precession_control_coefficient(self):
        return self.GTO.dSB_precessionControlCoefficient.value()

    def get_starting_speed_HF(self):
        return self.GTO.dSB_startingSpeedHF.value()

    def get_finished_speed_HF(self):
        return self.GTO.dSB_finishedSpeedHF.value()

    def set_start_point(self, x, y, z):
        self.GTO.dSB_coordX.setValue(x)
        self.GTO.dSB_coordY.setValue(y)
        self.GTO.dSB_coordZ.setValue(z)

    def set_end_point(self, x, y, z):
        self.GTO.dSB_coordX1.setValue(x)
        self.GTO.dSB_coordY1.setValue(y)
        self.GTO.dSB_coordZ1.setValue(z)

    def set_start_velocity(self, v0):
        self.GTO.dSB_startV.setValue(v0)

    def set_start_horizontal_angle(self, horizontal_angle):
        self.GTO.dSB_startHorizontalAngle.setValue(horizontal_angle)

    def set_start_above_angle(self, above_angle):
        self.GTO.dSB_startAboveAngle.setValue(above_angle)

    def set_weight(self, weight):
        self.GTO.dSB_weight.setValue(weight)

    def set_frontal_cross_sectional_area(self, frontal_cross_sectional_area):
        self.GTO.dSB_frontalCrossSectionalArea.setValue(frontal_cross_sectional_area)

    def set_resistance_coefficient(self, resistance_coefficient):
        self.GTO.dSB_resistanceCoefficient.setValue(resistance_coefficient)

    def set_air_density(self, air_density):
        self.GTO.dSB_airDensity.setValue(air_density)

    def set_precession_control_coefficient(self, precession_control_coefficient):
        self.GTO.dSB_precessionControlCoefficient.setValue(precession_control_coefficient)

    def set_starting_speed_HF(self, starting_speed_HF):
        self.GTO.dSB_startingSpeedHF.setValue(starting_speed_HF)

    def set_finished_speed_HF(self, finished_speed_HF):
        self.GTO.dSB_finishedSpeedHF.setValue(finished_speed_HF)


