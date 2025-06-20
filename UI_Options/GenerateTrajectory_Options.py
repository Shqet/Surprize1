from PyQt6 import QtWidgets

from UI.GenerateTrajectory import Ui_Form


class GenerateTrajectoryOptions(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.GTO = Ui_Form()
        self.GTO.setupUi(self)