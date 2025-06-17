import time
from datetime import datetime, timedelta

from GPS.console_hack_management import get_hackrf_serial_numbers, HackRFTransferRunner, GPSProcessRunner
from GPS.coord_transformation import CoordinateSystem, generate_coordinate


def use_two_hack():
    device_numbers = get_hackrf_serial_numbers()
    print(device_numbers)
    device_index = 0

    if len(device_numbers) < 2:
        print("Нет доступных устройств HackRF. Проверьте, что HackRF Tools установлены и добавлены в PATH.")
        exit(1)

    start_time = datetime(2025, 2, 12, 0, 0, 0)
    # start_real_time = datetime.now()
    all_time = time.perf_counter()
    nmea_file = "nmea_strings.txt"
    output_file = "nmea_strings.bin"

    coordinates_enu = (0,0,0)
    while True:
        time_start = time.perf_counter()
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

        if output_file == "nmea_strings.bin":
            # nmea_file="nmea_strings.txt"
            output_file = "nmea_strings2.bin"
            device_index = 1
        else:
            # nmea_file="nmea_strings.txt"
            output_file = "nmea_strings.bin"
            device_index = 0
        # while hackRFRunner.is_running():
        #     pass  # или time.sleep(1)
        coordinates_enu=generate_coordinate(1, coordinates_enu)
        delta_start_time = time.perf_counter() - all_time
        GPSProcessRunner(
            ephemeris_file="brdc0430.25n",
            nmea_file=nmea_file,
            bitrate=8,
            output_file=output_file,
            sim_dir="GPS_SDR_SIM",
            start_time=(start_time + timedelta(seconds=delta_start_time)).strftime("%Y/%m/%d,%H:%M:%S.%f")
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
        time_end = time.perf_counter()
        # print(time_end - time_start)
        time.sleep(1 - (time_end - time_start))
        # hackRFRunner.wait()

        # GPSrunner.wait()

        # time_end = datetime.now()
        # start_time += time_end-time_start
        # time.sleep(2-(time_end-time_start).total_seconds())

if __name__ == "__main__":
    use_two_hack()

