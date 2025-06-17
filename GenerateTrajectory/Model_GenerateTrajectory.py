import numpy as np
from typing import List, Tuple

from PyQt6.QtCore import pyqtSignal, QObject


class ModelGenerateTrajectory(QObject):
    trajectory_changed = pyqtSignal(list)

    def __init__(self, g: float = 9.81, dt: float = 0.1) -> None:
        super().__init__()
        self.g: float = g
        self.dt: float = dt
        self.trajectory: List[Tuple[float, float, float]] = []

    def compute_trajectory(
        self,
        distance: float,
        v0: float,
        angle_surface_deg: float,
        angle_target_deg: float,
        maneuverability: float = 0.05,
        drag_coefficient: float = 0.01
    ) -> List[Tuple[float, float, float]]:
        """
        Вычисляет траекторию от (0,0,0) до (distance, 0, 0) с маневрированием.

        :param distance: расстояние до цели по оси X
        :param v0: начальная скорость
        :param angle_surface_deg: угол к горизонту (градусы)
        :param angle_target_deg: угол отклонения в горизонтальной плоскости (градусы)
        :param maneuverability: коэффициент маневренности
        :param drag_coefficient: коэффициент сопротивления воздуха
        :return: список координат траектории
        """

        pos: np.ndarray = np.array([0.0, 0.0, 0.0])
        end_point: np.ndarray = np.array([distance, 0.0, 0.0])
        trajectory: List[Tuple[float, float, float]] = [tuple(pos)]

        # Углы в радианах
        theta: float = np.radians(angle_surface_deg)
        phi: float = np.radians(angle_target_deg)

        # Начальный вектор скорости
        vx = np.cos(theta) * np.cos(phi)
        vy = np.cos(theta) * np.sin(phi)
        vz = np.sin(theta)
        velocity: np.ndarray = v0 * np.array([vx, vy, vz])

        while pos[2] >= 0 and np.linalg.norm(velocity) > 1.0:
            pos += velocity * self.dt
            trajectory.append(tuple(pos))

            # Гравитация
            velocity[2] -= self.g * self.dt

            # Сопротивление воздуха
            speed = np.linalg.norm(velocity)
            if speed > 0:
                drag_force = drag_coefficient * velocity
                velocity -= drag_force * self.dt

            # Маневрирование — корректировка направления без увеличения скорости
            to_target = end_point - pos
            dist_to_target = np.linalg.norm(to_target)
            if dist_to_target > 1e-6:
                to_target_unit = to_target / dist_to_target

                v_unit = velocity / speed
                correction_direction = to_target_unit - np.dot(to_target_unit, v_unit) * v_unit

                if np.linalg.norm(correction_direction) > 1e-6:
                    correction_unit = correction_direction / np.linalg.norm(correction_direction)
                    correction = maneuverability * speed * correction_unit
                    velocity += correction * self.dt
        self.trajectory_changed.emit(trajectory)
        self.trajectory = trajectory
        return trajectory


    def get_trajectory(self):
        return self.trajectory