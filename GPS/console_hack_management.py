import re
import sys
import time
import os
import subprocess
import threading
from datetime import datetime, timedelta


def get_hackrf_serial_numbers():
    try:
        result = subprocess.run(["hackrf_info"], capture_output=True, text=True, check=True)
        output = result.stdout

        # Находим все серийные номера
        serials = re.findall(r"Serial number:\s*([0-9a-fA-F]{32})", output)
        return serials

    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении hackrf_info:", e)
        return []
    except FileNotFoundError:
        print("Утилита hackrf_info не найдена. Убедитесь, что HackRF Tools установлены и добавлены в PATH.")
        return []

import os
import subprocess
import threading
import time


class GPSProcessRunner:
    def __init__(self, ephemeris_file, nmea_file, bitrate, output_file,
                 sim_dir="GPS_SDR_SIM", start_time=None):
        """
        :param ephemeris_file: Файл эфемерид (например, brdc0430.25n)
        :param nmea_file: Файл с NMEA-строками
        :param bitrate: Битрейт (например, 8)
        :param output_file: Имя выходного бинарного файла
        :param sim_dir: Папка, где лежит gps-sdr-sim.exe и входные файлы
        :param start_time: Время начала симуляции в формате 'YYYY/MM/DD,HH:MM:SS'
        """

        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        self.sim_dir = os.path.join(base_dir, sim_dir)
        # self.sim_dir = os.path.join(base_dir,"GPS", sim_dir)
        print("self.sim_dir: ", self.sim_dir)
        self.executable = os.path.join(self.sim_dir, "gps-sdr-sim.exe")


        self.ephemeris_file = os.path.join(self.sim_dir, ephemeris_file)
        self.nmea_file = os.path.join(self.sim_dir, nmea_file)
        self.bitrate = str(bitrate)
        self.output_file = os.path.join(self.sim_dir, output_file)
        self.start_time = start_time  # строка или None

        self.process = None

    def build_command(self):
        cmd = [
            self.executable,
            "-e", self.ephemeris_file,
            "-g", self.nmea_file,
            # "-g", "nmea_strings.txt",
            "-b", self.bitrate,
            "-o", self.output_file,
            "-d", "300"
        ]
        if self.start_time:
            cmd += ["-t", self.start_time]
        return cmd

    def _read_stream(self, stream, label):
        for line in iter(stream.readline, ''):
            if line:
                pass
                # print(f"[{label}] {line.strip()}")
        stream.close()

    def start(self):
        if not os.path.isfile(self.executable):
            raise FileNotFoundError(f"Исполняемый файл не найден: {self.executable}")

        command = self.build_command()
        print(f"Запуск команды: {' '.join(command)}")

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.sim_dir
        )

        # Запускаем чтение вывода в отдельных потоках
        threading.Thread(target=self._read_stream, args=(self.process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=self._read_stream, args=(self.process.stderr, "STDERR"), daemon=True).start()

    def is_running(self):
        return self.process and self.process.poll() is None

    def wait(self):
        if self.process:
            self.process.wait()
            print(f"Процесс завершен с кодом: {self.process.returncode}")
            return self.process.returncode
        return None

    def terminate(self):
        if self.process:
            self.process.terminate()
            print("Процесс принудительно завершен.")




class HackRFTransferRunner:
    def __init__(self, input_file, frequency=1575420000, sample_rate=2600000, antenna=1, tx_gain=0, working_dir=".", device_number:str = "0"):
        """
        :param input_file: Бинарный файл (например, nmea_strings.bin)
        :param frequency: Частота в Гц (по умолчанию 1575.42 МГц)
        :param sample_rate: Частота дискретизации
        :param antenna: 1 = включить антенну
        :param tx_gain: Уровень усиления (от 0 до 47)
        :param working_dir: Папка, где лежит файл и где будет запуск
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.working_dir = os.path.join(self.script_dir, working_dir)
        self.executable = "hackrf_transfer"  # предполагается, что в PATH

        self.input_file = os.path.join(self.working_dir, input_file)
        self.frequency = str(frequency)
        self.sample_rate = str(sample_rate)
        self.antenna = str(antenna)
        self.tx_gain = str(tx_gain)
        self.device_number = str(device_number)

        self.process = None

    def build_command(self):
        return [
            self.executable,
            "-t", self.input_file,
            "-f", self.frequency,
            "-s", self.sample_rate,
            "-a", self.antenna,
            "-x", self.tx_gain,
            "-d", self.device_number
        ]

    def _read_stream(self, stream, label):
        for line in iter(stream.readline, ''):
            if line:
                pass
                print(f"[{label}] {line.strip()}")
        stream.close()

    def start(self):
        if not os.path.isfile(self.input_file):
            raise FileNotFoundError(f"Файл передачи не найден: {self.input_file}")

        command = self.build_command()
        print(f"Запуск команды: {' '.join(command)}")

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.working_dir
        )

        threading.Thread(target=self._read_stream, args=(self.process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=self._read_stream, args=(self.process.stderr, "STDERR"), daemon=True).start()

    def is_running(self):
        return self.process and self.process.poll() is None

    def wait(self):
        if self.process:
            self.process.wait()
            print(f"Процесс завершен с кодом: {self.process.returncode}")
            return self.process.returncode
        return None

    def terminate(self):
        if self.process:
            self.process.terminate()
            print("Процесс принудительно завершен.")










if __name__ == "__main__":

    start_time = datetime(2025, 2, 12, 0, 0, 0)
    start_real_time = datetime.now()

    nmea_file = "nmea_strings.txt"
    output_file = "nmea_strings.bin"

    device_numbers = get_hackrf_serial_numbers()
    print(device_numbers)
    device_index = 0

    if len(device_numbers) <2:
        print("Нет доступных устройств HackRF. Проверьте, что HackRF Tools установлены и добавлены в PATH.")
        exit(1)


    while True:
        time_start = datetime.now()
        HackRFTransferRunner(
            input_file=output_file,
            frequency=1575420000,
            sample_rate=2600000,
            antenna=1,
            tx_gain=0,
            working_dir="GPS_SDR_SIM",
            device_number=device_numbers[device_index]
            # device_number="0000000000000000436c63dc2f0e4363"
        ).start()


        # hackRFRunner.start()

        if output_file=="nmea_strings.bin":
            # nmea_file="nmea_strings.txt"
            output_file="nmea_strings2.bin"
            device_index = 1
        else:
            # nmea_file="nmea_strings.txt"
            output_file="nmea_strings.bin"
            device_index = 0
        # while hackRFRunner.is_running():
        #     pass  # или time.sleep(1)

        delta_start_time = datetime.now() - start_real_time
        GPSProcessRunner(
            ephemeris_file="brdc0430.25n",
            nmea_file=nmea_file,
            bitrate=8,
            output_file=output_file,
            sim_dir="GPS_SDR_SIM",
            start_time = (start_time+delta_start_time).strftime("%Y/%m/%d,%H:%M:%S")
        ).start()

        # try:
        #     GPSrunner.start()
        #     while GPSrunner.is_running():
        #         time.sleep(0.01)
        #         print("Процесс работает...")
        #
        #
        # except Exception as e:
        #     print("Ошибка:", e)
        time_end = datetime.now()
        time.sleep(1-(time_end-time_start).total_seconds())
        # hackRFRunner.wait()


        # GPSrunner.wait()









        # time_end = datetime.now()
        # start_time += time_end-time_start
        # time.sleep(2-(time_end-time_start).total_seconds())