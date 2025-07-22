from datetime import datetime, timedelta, timezone


def generate_static_nmea(
        lat: float = 55.7558,
        lon: float = 37.6173,
        height: float = 180.0,
        duration_sec: int = 60,
        step_sec: float = 0.1,
        filepath: str = "GPS_SDR_SIM/nmea_strings.txt"
):
    """
    Генерирует NMEA-файл с фиксированной координатой (GGA), с частотой обновления, например, 10 Гц (0.1 с шаг).

    :param lat: широта
    :param lon: долгота
    :param height: высота над уровнем моря
    :param duration_sec: длительность симуляции (в секундах)
    :param step_sec: интервал между строками (например, 0.1 сек)
    :param filepath: путь к создаваемому файлу
    """

    def to_nmea_latlon(lat, lon):
        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lat_str = f"{lat_deg:02d}{lat_min:07.4f},{'N' if lat >= 0 else 'S'}"

        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60
        lon_str = f"{lon_deg:03d}{lon_min:07.4f},{'E' if lon >= 0 else 'W'}"
        return lat_str, lon_str

    lat_str, lon_str = to_nmea_latlon(lat, lon)
    start_time = datetime.now(timezone.utc)

    num_points = int(duration_sec / step_sec)

    with open(filepath, 'w') as f:
        for i in range(num_points):
            t = start_time + timedelta(seconds=i * step_sec)
            t_str = t.strftime("%H%M%S.%f")[:-4]  # формат HHMMSS.ss
            line = f"$GPGGA,{t_str},{lat_str},{lon_str},1,08,0.9,{height:.1f},M,0.0,M,,*47\n"
            f.write(line)

    print(f"[+] Сгенерирован файл статической точки ({num_points} строк, {step_sec:.1f} с шаг): {filepath}")


if __name__ == "__main__":
    generate_static_nmea(
        lat=55.7558,
        lon=37.6173,
        height=180.0,
        duration_sec=300,
        filepath="nmea_strings.txt"
    )