from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from GenerateTrajectory.Model_GenerateTrajectory import ModelGenerateTrajectory
from GenerateTrajectory.ViewGenerateTrajectory import ViewGenerateTrajectory


class ControllerGenerateTrajectory(QObject):
    def __init__(self, model: ModelGenerateTrajectory, view: ViewGenerateTrajectory):
        super().__init__()
        self.model = model
        self.view = view

        self.model.trajectory_changed.connect(self.view.update_trajectory)
        self.view.pB_calculate.clicked.connect(self.calculate_trajectory)
        self.view.pB_save.clicked.connect(self.save_trajectory)

    def calculate_trajectory(self):

        distance = self.view.get_distance()
        v0 = self.view.get_start_velocity()
        angle_surface = self.view.get_angle_surface()
        angle_target = self.view.get_angle_target()
        maneuverability = self.view.get_maneuverability()
        drag_coefficient = self.view.get_drag_coefficient()

        self.model.compute_trajectory(distance, v0, angle_surface, angle_target, maneuverability, drag_coefficient)


    def save_trajectory(self):
        save_path,_ = QFileDialog.getSaveFileName(self.view.form, "Save Trajectory", "", "TXT Files (*.txt)")
        if save_path:
            with open(save_path, 'w') as file:
                for _ in range(900):
                    file.write("0,0,0\n")
                for point in self.model.get_trajectory():
                    file.write(f"{point[0]},{point[1]},{point[2]}\n")

        QMessageBox.information(
            self.view.form,
            "Внимание!",
            "Файл "+ save_path.split("/")[-1] +" успешно сохранен"
        )
