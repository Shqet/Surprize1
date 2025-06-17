import sys

from PyQt6.QtWidgets import QApplication

from GenerateTrajectory.Controller_GenerateTrajectory import ControllerGenerateTrajectory
from GenerateTrajectory.Model_GenerateTrajectory import ModelGenerateTrajectory
from GenerateTrajectory.ViewGenerateTrajectory import ViewGenerateTrajectory

if __name__ == "__main__":

    app = QApplication(sys.argv)

    model = ModelGenerateTrajectory()
    view = ViewGenerateTrajectory()
    controller = ControllerGenerateTrajectory(model, view)

    view.show()
    sys.exit(app.exec())