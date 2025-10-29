#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поллер скорости и позиции осей через УЧПУ «Маяк» по SSH.
Считывает CoE (SDO) у приводов по EtherCAT с помощью утилиты `ethercat upload`
(обычно предустановлена на Маяк). Для каждой оси задаётся адрес слейва и объекты
для скорости/позиции (по документации приводов: скорость — 0x6044:0 у большинства;
позиция — 0x6064:0 или, например, 0x2C49:3 у Lenze i550).

Зависимости на вашем ПК:  pip install paramiko
Как использовать: заполните конфиг ниже и запустите.
"""

import time
import csv
import threading
from datetime import datetime, timezone
import paramiko

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К МАЯК ---
MAYAK_HOST = "192.168.0.201"
MAYAK_USER = "developer"   # по инструкции для SSH в «конфигуратор»
MAYAK_PASS = "de"

# --- ОПИСАНИЕ ОСЕЙ/ПРИВОДОВ ---
# Каждая запись: человекочитаемое имя, адрес слейва EtherCAT (позиция -p),
# SDO для скорости (vel_obj=(0x6044, 0)) и для позиции (pos_obj=(индекс, субиндекс)).
# Примеры: Lenze i550 — pos_obj=(0x2C49, 3); большинство — (0x6064, 0)
DRIVES = [
    {"name": "X (Lenze i550)", "ecat_pos": 0, "vel_obj": (0x6044, 0), "pos_obj": (0x2C49, 3)},
    {"name": "Y (MR-J4)",      "ecat_pos": 1, "vel_obj": (0x6044, 0), "pos_obj": (0x6064, 0)},
    {"name": "Z (Accurax G5)", "ecat_pos": 2, "vel_obj": (0x6044, 0), "pos_obj": (0x6064, 0)},
    # Добавляйте оси по необходимости…
]

# --- ПАРАМЕТРЫ ОПРОСА ---
SAMPLE_HZ = 10.0              # частота опроса (Гц)
CSV_PATH  = "mayak_telemetry.csv"
TIMEOUT_SSH_CMD = 2.0         # таймаут на единичный вызов `ethercat upload`, c

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def ssh_run(client: paramiko.SSHClient, cmd: str) -> str:
    """Выполняет команду на Маяке и возвращает stdout как строку."""
    stdin, stdout, stderr = client.exec_command(cmd, timeout=TIMEOUT_SSH_CMD)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if err and not out:
        # Некоторые версии `ethercat` пишут предупреждения в stderr — не прерываемся, но возвращаем всё
        return (out + "\n" + err).strip()
    return out

def parse_ethercat_upload(output: str) -> int:
    """
    Разбирает типичные ответы `ethercat upload`.
    Утилита часто печатает число в десятичном виде (иногда с шапкой).
    Возвращаем int; если не удалось — бросаем ValueError.
    """
    # Берём последнюю непустую строку и пробуем прочитать десятичное либо 0x... шестнадцатеричное
    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("empty ethercat output")
    last = lines[-1]
    # Удалим служебное 'OK' и пр.
    for bad in ("OK",):
        if last.upper() == bad:
            if len(lines) >= 2:
                last = lines[-2]
            break
    # Попытка как десятичного
    try:
        return int(last, 10)
    except Exception:
        pass
    # Попытка выделить 0xHEX
    import re
    m = re.search(r'(0x[0-9A-Fa-f]+)', last)
    if m:
        return int(m.group(1), 16)
    # Попытка выдернуть финальное число
    m = re.search(r'(-?\d+)$', last)
    if m:
        return int(m.group(1), 10)
    raise ValueError(f"cannot parse ethercat output: {output!r}")

def make_upload_cmd(ecat_pos: int, index: int, sub: int) -> str:
    """
    Команда чтения SDO: ethercat upload -p <ecat_pos> <index> <sub>
    Некоторые установки используют `ethercat` без root; при необходимости добавьте 'sudo '.
    """
    return f"ethercat upload -p {ecat_pos} {hex(index)} {sub}"

# --- ОСНОВНАЯ ЛОГИКА ОПРОСА ---

class MayakPoller:
    def __init__(self, host, user, password, drives):
        self.host = host
        self.user = user
        self.password = password
        self.drives = drives
        self.client = None
        self.stop_flag = False
        self.lock = threading.Lock()

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, username=self.user, password=self.password, timeout=5)

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def read_drive(self, d):
        """Читает скорость и позицию одного привода, возвращает (vel, pos) как int."""
        vel_cmd = make_upload_cmd(d["ecat_pos"], *d["vel_obj"])
        pos_cmd = make_upload_cmd(d["ecat_pos"], *d["pos_obj"])

        # --- выполняем команды ---
        vel_raw_txt = ssh_run(self.client, vel_cmd)
        pos_raw_txt = ssh_run(self.client, pos_cmd)

        # --- выводим нераспаршенные ответы в консоль ---
        print(f"\n[{d['name']}] raw velocity:\n{vel_raw_txt}")
        print(f"[{d['name']}] raw position:\n{pos_raw_txt}")

        # --- парсим числовые значения ---
        try:
            vel_raw = parse_ethercat_upload(vel_raw_txt)
        except Exception as e:
            print(f"[WARN] {d['name']} velocity parse failed: {e}")
            vel_raw = None
        try:
            pos_raw = parse_ethercat_upload(pos_raw_txt)
        except Exception as e:
            print(f"[WARN] {d['name']} position parse failed: {e}")
            pos_raw = None

        return vel_raw, pos_raw

    def loop(self, sample_hz: float, csv_path: str):
        period = 1.0 / sample_hz
        # Подготовим CSV
        fieldnames = ["ts_iso"]
        for d in self.drives:
            fieldnames += [f"{d['name']}_vel", f"{d['name']}_pos"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            while not self.stop_flag:
                t0 = time.time()
                row = {"ts_iso": datetime.now(timezone.utc).isoformat(timespec="milliseconds")}
                for d in self.drives:
                    try:
                        vel, pos = self.read_drive(d)
                    except Exception as e:
                        vel = pos = None
                    row[f"{d['name']}_vel"] = vel
                    row[f"{d['name']}_pos"] = pos
                writer.writerow(row)
                f.flush()
                # поддерживаем частоту
                dt = time.time() - t0
                time.sleep(max(0.0, period - dt))

    def start(self, sample_hz: float, csv_path: str):
        self.connect()
        try:
            self.loop(sample_hz, csv_path)
        finally:
            self.close()

if __name__ == "__main__":
    poller = MayakPoller(MAYAK_HOST, MAYAK_USER, MAYAK_PASS, DRIVES)
    try:
        print(f"Старт опроса {len(DRIVES)} привод(ов) @ {SAMPLE_HZ} Гц. Лог: {CSV_PATH}")
        poller.start(SAMPLE_HZ, CSV_PATH)
    except KeyboardInterrupt:
        print("\nОстановка…")
        poller.stop_flag = True
        time.sleep(0.2)
        poller.close()
