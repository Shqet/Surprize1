import numpy as np
from typing import List, Tuple

from PyQt6.QtCore import pyqtSignal, QObject


class Model(QObject):
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

    def simulate_guided_trajectory(
            m: float,  # масса тела, кг
            S: float,  # лобовая площадь, м²
            C_D: float,  # коэффициент аэродинамического сопротивления
            start: Tuple[float, float, float],  # начальная точка (x, y, z)
            target: Tuple[float, float, float],  # точка назначения (x, y, z)
            v0: Tuple[float, float, float],  # начальная скорость (vx, vy, vz)
            g: float = 9.81,  # ускорение свободного падения, м/с²
            wind_zones: Optional[List[Tuple[float, float, Tuple[float, float, float]]]] = None,
            k_c: float = 2.0,  # максимальное корректирующее ускорение, м/с²
            p: float = 2  # степень убывания управляющего ускорения
    ) -> List[Tuple[float, float, float]]:
        """
        Симулирует траекторию управляемого тела с аэродинамическим торможением,
        корректировкой направления и учётом ветра. Возвращает список координат
        центра масс до достижения высоты целевой точки.
        """

        # Атмосферные параметры
        rho_0: float = 1.225  # плотность воздуха на уровне моря, кг/м³
        H: float = 8500.0  # масштабная высота атмосферы, м
        v0_mag: float = np.linalg.norm(v0)  # модуль начальной скорости

        def air_density(z: float) -> float:
            """Возвращает плотность воздуха в зависимости от высоты."""
            return rho_0 * np.exp(-z / H)

        def wind_at_altitude(z: float) -> np.ndarray:
            """
            Возвращает вектор ветра на данной высоте.
            Если высота попадает в одну из заданных зон, применяется соответствующий ветер.
            """
            if wind_zones:
                for z_min, z_max, wind_vec in wind_zones:
                    if z_min <= z <= z_max:
                        return np.array(wind_vec, dtype=np.float64)
            return np.zeros(3)

        def dynamics(t: float, Y: np.ndarray) -> List[float]:
            """
            Основная функция для интегратора. Вычисляет производные
            по времени для положения и скорости тела.
            """
            # Распаковка текущего состояния
            x, y, z, vx, vy, vz = Y
            pos: np.ndarray = np.array([x, y, z], dtype=np.float64)
            vel: np.ndarray = np.array([vx, vy, vz], dtype=np.float64)
            v_mag: float = np.linalg.norm(vel)

            # Относительная скорость с учётом ветра
            wind: np.ndarray = wind_at_altitude(z)
            v_rel: np.ndarray = vel - wind
            v_rel_mag: float = np.linalg.norm(v_rel)

            # Аэродинамическое сопротивление
            if v_rel_mag > 0:
                rho: float = air_density(z)
                F_drag: np.ndarray = 0.5 * rho * C_D * S * v_rel_mag * v_rel
                a_drag: np.ndarray = -F_drag / m
            else:
                a_drag = np.zeros(3)

            # Сила тяжести (вниз)
            a_gravity: np.ndarray = np.array([0, 0, -g], dtype=np.float64)

            # Корректирующее боковое ускорение, направленное в сторону цели
            d_target: np.ndarray = np.array(target) - pos

            if v_mag > 1e-2:
                v_dir: np.ndarray = vel / v_mag
                d_proj: np.ndarray = d_target - np.dot(d_target, v_dir) * v_dir  # перпендикуляр к скорости
                d_proj_norm: float = np.linalg.norm(d_proj)

                if d_proj_norm > 1e-6:
                    acc_dir: np.ndarray = d_proj / d_proj_norm
                    scale: float = (v_mag / v0_mag) ** p
                    a_corr: np.ndarray = k_c * min(1.0, scale) * acc_dir
                else:
                    a_corr = np.zeros(3)
            else:
                a_corr = np.zeros(3)

            # Общий вектор ускорения
            a_total: np.ndarray = a_drag + a_gravity + a_corr
            return [vx, vy, vz, *a_total]

        def reach_target_altitude(t: float, Y: np.ndarray) -> float:
            """
            Условие завершения симуляции: когда тело достигает высоты целевой точки.
            """
            return Y[2] - target[2]

        reach_target_altitude.terminal = True
        reach_target_altitude.direction = -1

        # Начальные условия
        Y0: List[float] = [*start, *v0]

        # Интеграция системы уравнений
        sol = solve_ivp(
            fun=dynamics,
            t_span=(0, 1e3),  # большое время, реальное завершение — через event
            y0=Y0,
            events=reach_target_altitude,
            max_step=0.05,  # шаг по времени (точность)
            rtol=1e-6,
            atol=1e-8,
        )

        # Возвращаем список координат траектории
        return list(zip(sol.y[0], sol.y[1], sol.y[2]))




    def get_trajectory(self):
        return self.trajectory

    def set_trajectory(self, trajectory:List[Tuple[float, float, float]]):
        self.trajectory = trajectory
        self.trajectory_changed.emit(self.trajectory)