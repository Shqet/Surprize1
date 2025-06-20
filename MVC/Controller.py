from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6 import QtWidgets

from MVC.Model import Model
from MVC.View import View


class Controller(QObject):
    def __init__(self, model: Model, view: View):
        super().__init__()



        self.model = model
        self.view = view



        self.model.trajectory_changed.connect(self.view.update_trajectory)

        self.view.a_loadTrajectory.triggered.connect(self.load_trajectory)
        self.view.a_saveTrajectory.triggered.connect(self.save_trajectory)
        self.view.a_showGenerateTrajectoryPage.triggered.connect(self.view.show_generate_trajectory_page)
        self.view.a_showTranslation.triggered.connect(self.view.show_translate_page)
        self.view.connect_to_change_trajectory_parameters(self.calculate_trajectory)
        self.calculate_trajectory()

    def calculate_trajectory(self):

        distance = self.view.get_distance()
        v0 = self.view.get_start_velocity()
        angle_surface = self.view.get_angle_surface()
        angle_target = self.view.get_angle_target()
        maneuverability = self.view.get_maneuverability()
        drag_coefficient = self.view.get_drag_coefficient()

        self.model.compute_trajectory(distance, v0, angle_surface, angle_target, maneuverability, drag_coefficient)


    def load_trajectory(self):
        file_path, _ = QFileDialog.getOpenFileName(self.view.form, "Load Trajectory", "", "TXT Files (*.txt)")
        if file_path:

            with open(file_path, 'r') as file:
                try:
                    lines = file.readlines()
                    distance = float(lines[0].split(":")[1].strip())
                    v0 = float(lines[1].split(":")[1].strip())
                    angle_surface = float(lines[2].split(":")[1].strip())
                    angle_target = float(lines[3].split(":")[1].strip())
                    maneuverability = float(lines[4].split(":")[1].strip())
                    drag_coefficient = float(lines[5].split(":")[1].strip())
                    trajectory = []

                    for line in lines[6:]:
                        x, y, z = map(float, line.split(","))
                        trajectory.append((x, y, z))
                except UnicodeDecodeError:
                    QMessageBox.information(
                        self.view.form,
                        "Ошибка!",
                        "Файл " + file_path.split("/")[-1] + " поврежден!"
                    )
                    return
                except ValueError:
                    QMessageBox.information(
                        self.view.form,
                        "Ошибка!",
                        "Файл " + file_path.split("/")[-1] + " поврежден!"
                    )
                    return
                except IndexError:
                    QMessageBox.information(
                        self.view.form,
                        "Ошибка!",
                        "Файл " + file_path.split("/")[-1] + " поврежден!"
                    )
                    return


                self.model.set_trajectory(trajectory)

                self.view.p_generateTrajectory.GTO.dSB_distance.setValue(distance)
                self.view.p_generateTrajectory.GTO.dSB_startV.setValue(v0)
                self.view.p_generateTrajectory.GTO.dSB_startHorizontalAngle.setValue(angle_surface)
                self.view.p_generateTrajectory.GTO.dSB_startAboveAngle.setValue(angle_target)
                self.view.p_generateTrajectory.GTO.dSB_maneuverability.setValue(maneuverability)
                self.view.p_generateTrajectory.GTO.dSB_dragCoefficient.setValue(drag_coefficient)
            self.view.set_opened_filename(file_path)
                # self.model.compute_trajectory(distance, v0, angle_surface, angle_target, maneuverability, drag_coefficient)

    def save_trajectory(self):
        distance = self.view.get_distance()
        v0 = self.view.get_start_velocity()
        angle_surface = self.view.get_angle_surface()
        angle_target = self.view.get_angle_target()
        maneuverability = self.view.get_maneuverability()
        drag_coefficient = self.view.get_drag_coefficient()



        save_path,_ = QFileDialog.getSaveFileName(self.view.form, "Save Trajectory", "", "TXT Files (*.txt)")
        if save_path:
            with open(save_path, 'w') as file:
                file.write(f"Дистанция: {distance}\nНачальная скорость: {v0}\nУгол к горизонту: {angle_surface}\nУгол отклонения в горизонтальной плоскости: {angle_target}\nКоэффициент маневренности: {maneuverability}\nКоэффициент сопротивления воздуха: {drag_coefficient}\n")
                # for _ in range(900):
                #     file.write("0.0,0.0,0.0\n")
                for point in self.model.get_trajectory():
                    file.write(f"{point[0]},{point[1]},{point[2]}\n")
            self.view.set_opened_filename(save_path)
            QMessageBox.information(
                self.view.form,
                "Внимание!",
                "Файл "+ save_path.split("/")[-1] +" успешно сохранен"
            )

    def show(self):
        self.view.show()
