import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta
from PyQt6.QtCore import pyqtSignal, QObject
import __main__, os

class Model(QObject):
    trajectory_changed = pyqtSignal(list)
    straight_trajectory_changed = pyqtSignal(list)

    def __init__(self, g: float = 9.81, dt: float = 0.1) -> None:
        super().__init__()

        self.straight_trajectory = None
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
            drag_coefficient: float = 0.01,
            accel_phase: float = 2.0  # время разгона до v0 (секунды)
    ) -> List[Tuple[float, float, float]]:
        """
        Вычисляет траекторию от (0,0,0) до (distance, 0, 0) с маневрированием.
        Добавлен разгон: в течение accel_phase секунд скорость возрастает от 0 до v0.

        :param distance: расстояние до цели по оси X
        :param v0: конечная скорость после разгона
        :param angle_surface_deg: угол к горизонту (градусы)
        :param angle_target_deg: угол отклонения в горизонтальной плоскости (градусы)
        :param maneuverability: коэффициент маневренности
        :param drag_coefficient: коэффициент сопротивления воздуха
        :param accel_phase: длительность разгона в секундах
        :return: список координат траектории
        """

        pos: np.ndarray = np.array([0.0, 0.0, 0.0])
        end_point: np.ndarray = np.array([distance, 0.0, 0.0])
        trajectory: List[Tuple[float, float, float]] = [tuple(pos)]

        # Углы в радианах
        theta: float = np.radians(angle_surface_deg)
        phi: float = np.radians(angle_target_deg)

        # Направление движения
        dir_vec = np.array([
            np.cos(theta) * np.cos(phi),
            np.cos(theta) * np.sin(phi),
            np.sin(theta)
        ])

        # Начальная скорость = 0
        velocity: np.ndarray = np.zeros(3)

        t = 0.0
        while pos[2] >= 0 and np.linalg.norm(velocity) > 0.1 or t < accel_phase:
            pos += velocity * self.dt
            trajectory.append(tuple(pos))

            # --- Разгонная фаза ---
            if t < accel_phase:
                # линейный рост скорости от 0 до v0
                target_speed = v0 * (t / accel_phase)
                current_speed = np.linalg.norm(velocity)
                dv = target_speed - current_speed
                if dv > 0:
                    velocity += dir_vec * (dv / max(self.dt, 1e-9))
            else:
                # Гравитация
                velocity[2] -= self.g * self.dt

                # Сопротивление воздуха
                speed = np.linalg.norm(velocity)
                if speed > 0:
                    drag_force = drag_coefficient * velocity
                    velocity -= drag_force * self.dt

                # Маневрирование
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

            t += self.dt

        self.trajectory_changed.emit(trajectory)
        self.trajectory = trajectory
        return trajectory

    def generate_straight_trajectory(self,speed: float, distance: float, step: float = 0.1) -> List[Tuple[float, float, float]]:
        """
        Генерация траектории движения по прямой.

        :param speed: скорость (м/с)
        :param distance: дистанция (м)
        :param step: шаг по времени (сек), по умолчанию 1 секунда
        :return: список точек [(x, y, t)]
        """
        trajectory = []
        total_time = distance / speed
        t = 0.0

        while t <= total_time:
            x = speed * t
            trajectory.append((x, 0.0, 0.0))
            t += step

        # Добавим конечную точку точно в distance
        if trajectory[-1][0] < distance:
            trajectory.append((distance, 0.0, 0.0))
        self.straight_trajectory_changed.emit(trajectory)
        self.straight_trajectory = trajectory
        return trajectory

    def get_straight_trajectory(self):
        return self.straight_trajectory

    import numpy as np

    def simulate_guided_flight_with_strong_control(self,
                                                   r0, r_target, v0, theta0_deg, phi0_deg,
                                                   mass, S, C_D, rho, l_m,
                                                   omega_spin_0, k_cp, k_guidance,
                                                   Ix=0.01, Iy=0.002, Iz=0.002,
                                                   dt=0.005, g=9.81
                                                   ):
        """
        Сбалансированная модель полета снаряда с уравнениями Эйлера (10.9) и активным управлением.
        Включает ограничения, достаточные для стабильности, но позволяющие маневрировать.
        """

        r = np.array(r0, dtype=np.float64)
        traj = [tuple(r)]

        theta = np.radians(theta0_deg)
        phi = np.radians(phi0_deg)
        dir0 = np.array([
            np.cos(theta) * np.cos(phi),
            np.cos(theta) * np.sin(phi),
            np.sin(theta)
        ])
        v = v0 * dir0

        # Угловые скорости
        omega_x = omega_spin_0
        omega_y = omega_z = 0.0
        # Отклонения ориентации
        delta_y = delta_z = 0.0

        z_target = r_target[2]
        has_reached_apex = False

        for step in range(200000):
            t = step * dt
            speed = np.linalg.norm(v)
            if speed < 1e-3:
                break

            # Аэродинамические и управляющие моменты
            Mx = -Ix * k_cp * omega_x
            My_aero = -rho * speed ** 2 * S * l_m * delta_y / 2
            Mz_aero = -rho * speed ** 2 * S * l_m * delta_z / 2

            to_target = np.array(r_target) - r
            to_target /= np.linalg.norm(to_target)
            velocity_dir = v / speed
            error = to_target - velocity_dir
            error = np.clip(error, -1.0, 1.0)  # до ±1 рад (≈ 57°)

            My_control = -k_guidance * error[1]
            Mz_control = -k_guidance * error[2]
            My = My_aero + My_control
            Mz = Mz_aero + Mz_control

            # Уравнения Эйлера
            domega_x = Mx / Ix
            domega_y = (My - (Iz - Ix) * omega_z * omega_x) / Iy
            domega_z = (Mz - (Ix - Iy) * omega_x * omega_y) / Iz

            if not np.isfinite(domega_y) or not np.isfinite(domega_z):
                break

            omega_x += domega_x * dt
            omega_y += domega_y * dt
            omega_z += domega_z * dt

            # Ограничения на угловые скорости
            omega_x = np.clip(omega_x, -15000, 15000)
            omega_y = np.clip(omega_y, -2000, 2000)
            omega_z = np.clip(omega_z, -2000, 2000)

            # Интеграция углов ориентации
            delta_y += omega_y * dt
            delta_z += omega_z * dt

            # Ограничения на углы ориентации
            delta_y = np.clip(delta_y, -1.0, 1.0)
            delta_z = np.clip(delta_z, -1.0, 1.0)

            # Ось тела
            body_dir = velocity_dir + np.array([0, delta_y, delta_z])
            norm_bd = np.linalg.norm(body_dir)
            if norm_bd < 1e-6:
                body_dir = velocity_dir
            else:
                body_dir /= norm_bd

            # Силы
            F_aero = -0.5 * rho * C_D * S * speed * body_dir
            F_grav = np.array([0, 0, -mass * g])
            a_lin = (F_aero + F_grav) / mass

            # Интеграция поступательного движения
            v += a_lin * dt
            r += v * dt
            traj.append(tuple(r))

            # Условие завершения
            if not has_reached_apex and v[2] < 0:
                has_reached_apex = True
            if has_reached_apex and r[2] <= z_target:
                break

        self.trajectory = traj
        self.trajectory_changed.emit(traj)
        return traj



    def get_trajectory(self):
        return self.trajectory

    def set_trajectory(self, trajectory:List[Tuple[float, float, float]]):
        self.trajectory = trajectory
        self.trajectory_changed.emit(self.trajectory)

    def export_trajectory_to_nmea(self, step_sec: float = 0.1, delay_sec: float = 0.0):
        """
        Экспорт текущей траектории в NMEA-формат с учётом задержки.
        Файл сохраняется в ту же папку, где лежит gps-sdr-sim.exe.
        """
        if not self.trajectory:
            raise ValueError("Траектория пуста")

        import os
        import sys
        from datetime import datetime, timedelta, timezone

        # Определим путь к GPS_SDR_SIM
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__main__.__file__))

        sim_dir = os.path.join(base_dir, "GPS","GPS_SDR_SIM")
        filepath = os.path.join(sim_dir, "nmea_strings.txt")

        # Убедимся, что папка существует (на случай запуска не из PyInstaller)
        os.makedirs(sim_dir, exist_ok=True)

        def to_nmea_latlon(lat, lon):
            lat_deg = int(abs(lat))
            lat_min = (abs(lat) - lat_deg) * 60
            lat_str = f"{lat_deg:02d}{lat_min:07.4f},{'N' if lat >= 0 else 'S'}"

            lon_deg = int(abs(lon))
            lon_min = (abs(lon) - lon_deg) * 60
            lon_str = f"{lon_deg:03d}{lon_min:07.4f},{'E' if lon >= 0 else 'W'}"
            return lat_str, lon_str

        start_time = datetime.now(timezone.utc)

        with open(filepath, 'w') as f:
            for i, (x, y, z) in enumerate(self.trajectory):
                lat, lon, h = 55.0 + x * 1e-5, 37.0 + y * 1e-5, z
                t = start_time + timedelta(seconds=i * step_sec)
                t_str = t.strftime("%H%M%S.%f")[:-4]
                lat_str, lon_str = to_nmea_latlon(lat, lon)
                f.write(f"$GPGGA,{t_str},{lat_str},{lon_str},1,08,0.9,{h:.1f},M,0.0,M,,*47\n")

        print(f"[+] Экспортировано в {filepath}")
        self.prepend_static_padding_to_nmea(filepath, delay_sec=delay_sec, step_sec=step_sec)

    @staticmethod
    def prepend_static_padding_to_nmea(
            filepath: str = "GPS_SDR_SIM/nmea_strings.txt",
            delay_sec: float = 30.0,
            step_sec: float = 0.1
    ):
        """
        Дополняет nmea_strings.txt в начале фиксированными строками, чтобы добавить задержку delay_sec.
        """
        with open(filepath, "r") as f:
            lines = f.readlines()

        target_lines = int(delay_sec / step_sec)

        # if len(lines) >= target_lines:
        #     print(f"[=] Уже {len(lines)} строк, не требует дополнения.")
        #     return

        # Извлечём первую строку как шаблон
        first_line = lines[0].strip()
        time_str = first_line.split(",")[1]  # HHMMSS или HHMMSS.ss

        # Определим базовое UTC время из первой строки
        base_time = datetime.strptime(time_str[:6], "%H%M%S")

        # Остальные поля
        gga_rest = ",".join(first_line.split(",")[2:])

        missing_lines = target_lines

        # Генерация новых строк
        padding = []
        for i in range(missing_lines, 0, -1):
            t = base_time - timedelta(seconds=i * step_sec)
            t_str = t.strftime("%H%M%S.%f")[:-4]
            padding.append(f"$GPGGA,{t_str},{gga_rest}\n")

        # Сохраняем результат
        with open(filepath, "w") as f:
            f.writelines(padding + lines)

        print(f"[+] Добавлено {missing_lines} статичных строк. Общее число строк: {len(padding) + len(lines)}")
