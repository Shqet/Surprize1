import time
from datetime import datetime

from GPS.console_hack_management import get_hackrf_serial_numbers, HackRFTransferRunner, GPSProcessRunner
from GPS.coord_transformation import CoordinateSystem, generate_coordinate, generate_coordinate1


def use_one_hack_permanently():


    start_time = datetime(2025, 2, 12, 0, 0, 0)
    start_real_time = datetime.now()

    nmea_file = "nmea_strings.txt"
    output_file = "nmea_strings.bin"

    device_numbers = get_hackrf_serial_numbers()
    print(device_numbers)
    device_index = 0

    if len(device_numbers) < 1:
        print("Нет доступных устройств HackRF. Проверьте, что HackRF Tools установлены и добавлены в PATH.")
        exit(1)

    while True:
        delta_start_time = datetime.now() - start_real_time
        GPSrunner = GPSProcessRunner(
            ephemeris_file="brdc0430.25n",
            nmea_file=nmea_file,
            bitrate=8,
            output_file=output_file,
            sim_dir="GPS_SDR_SIM",
            start_time=(start_time + delta_start_time).strftime("%Y/%m/%d,%H:%M:%S")
        )
        GPSrunner.start()
        time_start = datetime.now()
        hackRFRunner = HackRFTransferRunner(
            input_file=output_file,
            frequency=1575420000,
            sample_rate=2600000,
            antenna=1,
            tx_gain=0,
            working_dir="GPS_SDR_SIM",
            device_number=device_numbers[device_index]
            # device_number="0000000000000000436c63dc2f0e4363"
        )
        hackRFRunner.start()

        # hackRFRunner.start()






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
        # time.sleep(1 - (time_end - time_start).total_seconds())
        hackRFRunner.wait()

        GPSrunner.wait()

        # time_end = datetime.now()
        # start_time += time_end-time_start
        # time.sleep(2-(time_end-time_start).total_seconds())

if __name__ == "__main__":
    generate_coordinate1(1000)
    use_one_hack_permanently()