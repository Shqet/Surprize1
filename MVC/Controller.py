import time

from PyQt6.QtCore import QObject, QTimer


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
        self.view.a_showGenerateStraightTrajectory.triggered.connect(self.view.show_generate_straight_trajectory_page)
        self.view.connect_to_change_trajectory_parameters(self.calculate_trajectory)
        self.view.p_translateSignal.GTO.pB_start_translation.clicked.connect(self.start_translation)
        # self.view.p_generateStraightTrajectory.pB_calculate_trajectory
        self.view.p_generateStraightTrajectory.GTO.pB_generate.clicked.connect(self.calculate_straight_trajectory)
        self.view.p_generateStraightTrajectory.GTO.pB_startTranslation.clicked.connect(self.translate_straight_trajectory)

        self.calculate_trajectory()

    def calculate_trajectory(self):

        distance = self.view.get_distance()
        v0 = self.view.get_start_velocity()
        angle_surface = self.view.get_angle_surface()
        angle_target = self.view.get_angle_target()
        maneuverability = self.view.get_maneuverability()
        drag_coefficient = self.view.get_drag_coefficient()

        self.model.compute_trajectory(distance, v0, angle_surface, angle_target, maneuverability, drag_coefficient)

    def new_calculate_trajectory(self):
        start_point = self.view.p_newGenerateTrajectory.get_start_point()
        end_point = self.view.p_newGenerateTrajectory.get_end_point()
        velocity = self.view.p_newGenerateTrajectory.get_start_velocity()
        start_horizontal_angle = self.view.p_newGenerateTrajectory.get_start_horizontal_angle()
        start_vertical_angle = self.view.p_newGenerateTrajectory.get_start_above_angle()

        weight = self.view.p_newGenerateTrajectory.get_weight()
        frontal_cross_sectional_area = self.view.p_newGenerateTrajectory.get_frontal_cross_sectional_area()
        resistance_coefficient = self.view.p_newGenerateTrajectory.get_resistance_coefficient()
        air_density = self.view.p_newGenerateTrajectory.get_air_density()
        precession_control_coefficient = self.view.p_newGenerateTrajectory.get_precession_control_coefficient()

        self.model.simulate_guided_flight_with_strong_control(start_point, end_point, velocity, start_horizontal_angle, start_vertical_angle, weight, frontal_cross_sectional_area, resistance_coefficient, air_density,0.4,300,0.1, precession_control_coefficient)

    def load_trajectory(self):
        file_path = self.view.ask_open_file_path()
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                distance = float(lines[0].split(":")[1].strip())
                v0 = float(lines[1].split(":")[1].strip())
                angle_surface = float(lines[2].split(":")[1].strip())
                angle_target = float(lines[3].split(":")[1].strip())
                maneuverability = float(lines[4].split(":")[1].strip())
                drag_coefficient = float(lines[5].split(":")[1].strip())

                trajectory = [
                    tuple(map(float, line.split(",")))
                    for line in lines[6:]
                ]
        except (UnicodeDecodeError, ValueError, IndexError):
            self.view.show_error(f"Файл {file_path.split('/')[-1]} повреждён.")
            return

        self.model.set_trajectory(trajectory)
        self.view.set_opened_filename(file_path)
        self.view.set_distance(distance)
        self.view.set_start_velocity(v0)
        self.view.set_angle_surface(angle_surface)
        self.view.set_angle_target(angle_target)
        self.view.set_maneuverability(maneuverability)
        self.view.set_drag_coefficient(drag_coefficient)

    def save_trajectory(self):
        file_path = self.view.ask_save_file_path()
        if not file_path:
            return

        try:
            with open(file_path, 'w') as file:
                file.write(f"Дистанция: {self.view.get_distance()}\n")
                file.write(f"Начальная скорость: {self.view.get_start_velocity()}\n")
                file.write(f"Угол к горизонту: {self.view.get_angle_surface()}\n")
                file.write(f"Угол отклонения в горизонтальной плоскости: {self.view.get_angle_target()}\n")
                file.write(f"Коэффициент маневренности: {self.view.get_maneuverability()}\n")
                file.write(f"Коэффициент сопротивления воздуха: {self.view.get_drag_coefficient()}\n")
                for point in self.model.get_trajectory():
                    file.write(f"{point[0]},{point[1]},{point[2]}\n")
        except Exception as e:
            self.view.show_error(f"Ошибка сохранения: {str(e)}")
            return

        self.view.set_opened_filename(file_path)
        self.view.show_info(f"Файл {file_path.split('/')[-1]} успешно сохранён.")

    def show(self):
        self.view.show()

    def start_translation(self):
        try:
            # Получаем значение задержки из GUI
            delay_sec = self.view.p_translateSignal.GTO.dSB_delay.value()

            # Экспорт траектории в NMEA с учётом задержки
            self.model.export_trajectory_to_nmea(
                delay_sec=delay_sec
            )

        except Exception as e:
            self.view.show_error(f"Ошибка экспорта: {e}")
            return

        from datetime import datetime
        from GPS.console_hack_management import GPSProcessRunner, HackRFTransferRunner, get_hackrf_serial_numbers

        start_time = datetime(2025, 2, 12, 0, 0, 0)
        start_real_time = datetime.now()
        delta_start_time = datetime.now() - start_real_time

        device_numbers = get_hackrf_serial_numbers()
        if not device_numbers:
            self.view.show_error("HackRF не обнаружен.")
            return

        nmea_file = "nmea_strings.txt"
        output_file = "nmea_strings.bin"

        try:
            gps_runner = GPSProcessRunner(
                ephemeris_file="brdc0430.25n",
                nmea_file=nmea_file,
                bitrate=8,
                output_file=output_file,
                sim_dir="GPS_SDR_SIM",
                start_time=(start_time + delta_start_time).strftime("%Y/%m/%d,%H:%M:%S")
            )
            gps_runner.start()
            gps_runner.wait()

            hackrf_runner = HackRFTransferRunner(
                input_file=output_file,
                frequency=1575420000,
                sample_rate=2600000,
                antenna=1,
                tx_gain=10,
                working_dir="GPS_SDR_SIM",
                device_number=device_numbers[0]
            )
            hackrf_runner.start()

            self.animate_trajectory(
                self.view.p_translateSignal.GTO.widget,
                self.model.get_trajectory()
            )

        except Exception as e:
            self.view.show_error(f"Ошибка трансляции: {e}")

    import time
    from PyQt6.QtCore import QTimer

    import time
    from PyQt6.QtCore import QTimer

    def animate_trajectory(self, widget3d, trajectory: list[tuple[float, float, float]], step_ms=100):
        """
        Анимирует движение по траектории и отображает прошедшее время, с учётом задержки dSB_delay.
        """
        if not trajectory:
            return

        step_duration_sec = step_ms / 1000.0
        widget3d.start_translation()

        delay_sec = self.view.p_translateSignal.GTO.dSB_delay.value()  # задержка в секундах
        start_time = time.monotonic()  # старт отсчёта для отображения времени

        # === Таймер отображения времени ===
        time_timer = QTimer(widget3d)
        time_timer.setInterval(100)

        def update_time():
            elapsed = time.monotonic() - start_time
            try:
                self.view.p_translateSignal.GTO.l_translation_time.setText(f"{elapsed:05.1f} сек")
            except AttributeError:
                print("⚠️ l_translation_time не найден")

        time_timer.timeout.connect(update_time)
        time_timer.start()  # запуск сразу

        # === Таймер позиции ===
        pos_timer = QTimer(widget3d)
        pos_timer.setInterval(100)

        real_start_time = [None]

        def update_position():
            if real_start_time[0] is None:
                return
            self.view.p_translateSignal.GTO.l_sygnal.setStyleSheet("background-color: rgb(0, 255, 0)")
            elapsed = time.monotonic() - real_start_time[0]
            index = int(elapsed / step_duration_sec)
            if 0 <= index < len(trajectory):
                widget3d.update_position_marker(trajectory[index])
            elif index >= len(trajectory):
                pos_timer.stop()
                time_timer.stop()
                widget3d.stop_translation()
                self.view.p_translateSignal.GTO.l_sygnal.setStyleSheet("")

        pos_timer.timeout.connect(update_position)

        # Показать первую точку
        widget3d.update_position_marker(trajectory[0])

        # Старт таймера позиции после задержки
        def start_position_timer():
            real_start_time[0] = time.monotonic()
            pos_timer.start()

        QTimer.singleShot(int(delay_sec * 1000), start_position_timer)



    def calculate_straight_trajectory(self):
        speed = self.view.p_generateStraightTrajectory.GTO.dSB_speed.value()
        distance = self.view.p_generateStraightTrajectory.GTO.dSB_distance.value()
        trajectory = self.model.generate_straight_trajectory(speed, distance)
        self.view.p_generateStraightTrajectory.GTO.f_3DView.update_trajectory(trajectory)

    def translate_straight_trajectory(self):

        from datetime import datetime
        from GPS.console_hack_management import GPSProcessRunner, HackRFTransferRunner, get_hackrf_serial_numbers

        start_time = datetime(2025, 2, 12, 0, 0, 0)
        start_real_time = datetime.now()
        delta_start_time = datetime.now() - start_real_time

        device_numbers = get_hackrf_serial_numbers()
        if not device_numbers:
            self.view.show_error("HackRF не обнаружен.")
            return

        nmea_file = "nmea_strings.txt"
        output_file = "nmea_strings.bin"

        try:
            gps_runner = GPSProcessRunner(
                ephemeris_file="brdc0430.25n",
                nmea_file=nmea_file,
                bitrate=8,
                output_file=output_file,
                sim_dir="GPS_SDR_SIM",
                start_time=(start_time + delta_start_time).strftime("%Y/%m/%d,%H:%M:%S")
            )
            gps_runner.start()
            gps_runner.wait()

            hackrf_runner = HackRFTransferRunner(
                input_file=output_file,
                frequency=1575420000,
                sample_rate=2600000,
                antenna=1,
                tx_gain=10,
                working_dir="GPS_SDR_SIM",
                device_number=device_numbers[0]
            )
            hackrf_runner.start()

            self.animate_trajectory(
                self.view.p_generateStraightTrajectory.GTO.f_3DView,
                self.model.get_straight_trajectory()
            )

        except Exception as e:
            self.view.show_error(f"Ошибка трансляции: {e}")





