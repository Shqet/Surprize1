import numpy as np
from math import sin, cos, radians, sqrt, degrees
import time

# Параметры эллипсоида WGS84
a = 6378137.0  # Большая полуось (м)
e2 = 6.69437999014e-3  # Экспоненциальный эксцентриситет^2


class CoordinateSystem:
    def __init__(self):
        # Начальные координаты системы (широта, долгота, высота)
        self.lat0 = None
        self.lon0 = None
        self.h0 = None
        self.X0 = None
        self.Y0 = None
        self.Z0 = None

    def set_origin(self, lat, lon, h):
        """Устанавливает начало координат (широта, долгота, высота)."""
        self.lat0 = lat
        self.lon0 = lon
        self.h0 = h
        self.X0, self.Y0, self.Z0 = self.geodetic_to_ecef(lat, lon, h)

    def geodetic_to_ecef(self, lat, lon, h):
        """Преобразование геодезических координат (широта, долгота, высота) в ECEF."""
        lat = radians(lat)
        lon = radians(lon)

        N = a / sqrt(1 - e2 * sin(lat) ** 2)  # Радиус кривизны
        X = (N + h) * cos(lat) * cos(lon)
        Y = (N + h) * cos(lat) * sin(lon)
        Z = (N * (1 - e2) + h) * sin(lat)

        return X, Y, Z

    def ecef_to_enu(self, X, Y, Z):
        """Преобразование координат из ECEF в локальную систему ENU."""
        # Широта и долгота в радианах
        lat0 = radians(self.lat0)
        lon0 = radians(self.lon0)

        # Матрица поворота для ENU (East, North, Up) относительно (lat0, lon0)
        R = np.array([[-sin(lon0), cos(lon0), 0],
                      [-sin(lat0) * cos(lon0), -sin(lat0) * sin(lon0), cos(lat0)],
                      [cos(lat0) * cos(lon0), cos(lat0) * sin(lon0), sin(lat0)]])

        # Вектор от начала координат в ECEF до текущей точки
        dX = self.X0 - X
        dY = self.Y0 - Y
        dZ = self.Z0 - Z

        # Получаем координаты объекта в ENU
        enu = np.dot(R, np.array([dX, dY, dZ]))

        return enu

    def enu_to_ecef(self, x, y, z):
        """Преобразование координат из локальной системы ENU в ECEF."""
        # Широта и долгота в радианах
        lat0 = radians(self.lat0)
        lon0 = radians(self.lon0)

        # Матрица поворота для ENU (East, North, Up) относительно (lat0, lon0)
        R = np.array([[-sin(lon0), cos(lon0), 0],
                      [-sin(lat0) * cos(lon0), -sin(lat0) * sin(lon0), cos(lat0)],
                      [cos(lat0) * cos(lon0), cos(lat0) * sin(lon0), sin(lat0)]])

        # Преобразуем из локальной системы в глобальную
        ecef = np.dot(R.T, np.array([x, y, z]))

        return ecef

    def get_object_ecef(self, x, y, z):
        """Преобразование координат объекта из локальной системы (ENU) в глобальные (ECEF)."""
        # Переводим координаты объекта из локальной системы ENU в глобальную систему ECEF
        X, Y, Z = self.enu_to_ecef(x, y, z)

        # Возвращаем итоговые координаты объекта в системе ECEF
        return X + self.X0, Y + self.Y0, Z + self.Z0

    def geodetic_to_nmea(self, lat, lon, h):
        """Преобразование геодезических координат в строку NMEA GPGGA."""
        lat_deg = int(lat)
        lon_deg = int(lon)
        lat_min = (lat - lat_deg) * 60
        lon_min = (lon - lon_deg) * 60
        utc_time = time.strftime("%H%M%S", time.gmtime())

        # Формируем строку GPGGA
        nmea_str = f"$GPGGA,{utc_time},{lat_deg:02d}{lat_min:07.4f},{'N' if lat >= 0 else 'S'},"
        nmea_str += f"{lon_deg:03d}{lon_min:07.4f},{'E' if lon >= 0 else 'W'},1,08,0.9,{h:.1f},M,46.9,M,,*47"

        # Контрольная сумма
        nmea_str += "*" + hex(sum(ord(c) for c in nmea_str[1:]) & 0xFF)[2:].upper().zfill(2)

        return nmea_str

    def convert_enu_to_nmea(self, coordinates):
        """Преобразование массива координат ENU в NMEA строки."""
        nmea_strings = []

        for coord in coordinates:
            x, y, z = coord
            X, Y, Z = self.get_object_ecef(x, y, z)

            # Преобразуем ECEF в геодезические координаты
            lat, lon, h = self.ecef_to_geodetic(X, Y, Z)

            # Получаем строку NMEA
            nmea_str = self.geodetic_to_nmea(lat, lon, h)
            nmea_strings.append(nmea_str)

        return nmea_strings

    def ecef_to_geodetic(self, X, Y, Z):
        """Преобразование ECEF в геодезические координаты."""
        p = sqrt(X ** 2 + Y ** 2)
        lat = degrees(np.arctan2(Z, p * (1 - e2)))
        lon = degrees(np.arctan2(Y, X))
        h = 0  # Пример: добавим высоту как 0, для упрощения. Реальное значение можно найти через итерации.
        return lat, lon, h


def generate_coordinate(countsecond = 1, coordinates_enu = (0, 0, 0)):
    coord_sys = CoordinateSystem()
    coord_sys.set_origin(55.0, 37.0, 200)
    # coordinates_enu = (0, 0, 0)

    with open("GPS_SDR_SIM/nmea_strings.txt", "w") as file:
        for i in range(countsecond*10):
            # Массив локальных координат ENU
            nmea = coord_sys.geodetic_to_nmea(coordinates_enu[0], coordinates_enu[1], coordinates_enu[2])
            coordinates_enu += (coordinates_enu[0]+1, coordinates_enu[1]+0, coordinates_enu[2]+1)
            file.write(nmea + "\n")
    return coordinates_enu

def generate_coordinate1(countsecond = 1):
    coord_sys = CoordinateSystem()
    coord_sys.set_origin(55.0, 37.0, 200)
    coordinates_enu = (0, 0, 0)

    with open("GPS_SDR_SIM/nmea_strings.txt", "w") as f:
        for i in range(countsecond*10):
            # if i > 2000:
            # Массив локальных координат ENU
                nmea = coord_sys.geodetic_to_nmea(coordinates_enu[0], coordinates_enu[1], coordinates_enu[2])
                if i%2 == 0:
                    coordinates_enu = (coordinates_enu[0]+0.000001, coordinates_enu[1]+0, coordinates_enu[2]+0)
                f.write(nmea + "\n")
            # else:
            #     nmea = coord_sys.geodetic_to_nmea(coordinates_enu[0], coordinates_enu[1], coordinates_enu[2])
            #     # coordinates_enu = (coordinates_enu[0] + 1, coordinates_enu[1] + 0, coordinates_enu[0])
            #     f.write(nmea + "\n")
    # return coordinates_enu


if __name__ == "__main__":
    # Пример использования:
    coord_sys = CoordinateSystem()
    coord_sys.set_origin(55.0, 37.0, 200)
    coordinates_enu = (0,0,0)

    with open("GPS_SDR_SIM/nmea_strings.txt", "w") as file:
        for i in range(10):
        # Массив локальных координат ENU
            nmea = coord_sys.geodetic_to_nmea(coordinates_enu[0], coordinates_enu[1], coordinates_enu[2])
            coordinates_enu+=(0,0,0)
            file.write(nmea + "\n")

